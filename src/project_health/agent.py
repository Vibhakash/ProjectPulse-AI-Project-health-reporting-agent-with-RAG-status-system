from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from typing import Any

from .metrics import project_metrics
from .schemas import ProjectWorkbook, RagResult


AGENT_SYSTEM_PROMPT = """You are a Project Health Reporting Agent for a Professional Services leadership team.

Your job:
- Do NOT decide or change the RAG color — that is set by the deterministic rule engine and is final.
- Explain the RAG status in plain English using the evidence provided.
- Summarize stakeholder sentiment from comments ONLY when actual comments exist.
- Cite specific task source_row numbers or comment source_row numbers when making a claim.
- Identify emerging risk themes, blocker patterns, and practical next actions.
- Be honest about missing or messy data.
- Do NOT invent budget, comments, milestones, owners, or dates.
- Return valid JSON only — no markdown fences, no extra keys.
"""

# Agent mode constants
MODE_GROQ = "llm:groq"
MODE_OPENAI = "llm:openai"
MODE_ANTHROPIC = "llm:anthropic"
MODE_GEMINI = "llm:gemini"
MODE_OFFLINE = "offline"
MODE_FAILED = "llm_failed"


class ProjectHealthAgent:
    """
    AI agent layer that enriches deterministic RAG output with plain-English
    reasoning, stakeholder sentiment, risk themes, and recommendations.

    Provider priority (first one with a key wins):
      1. Groq (Llama 3.3 70B)  — FREE, 14,400 req/day, no credit card
      2. Gemini 1.5 Flash       — FREE, 1,500 req/day, no credit card
      3. OpenAI GPT-4o-mini     — paid
      4. Anthropic Claude        — paid

    IMPORTANT: If the configured LLM provider fails (bad key, quota, network),
    the agent sets agent_mode="llm_failed" and does NOT fall back to offline
    reasoning unless PROJECT_HEALTH_ALLOW_OFFLINE_FALLBACK=true is set in .env.
    """

    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        env_provider = os.getenv("PROJECT_HEALTH_LLM_PROVIDER", "").strip().lower()
        self.provider = (provider or env_provider or _detect_provider()).lower()
        self.model = model or os.getenv("PROJECT_HEALTH_LLM_MODEL", "").strip() or _default_model(self.provider)
        self.allow_offline_fallback = os.getenv("PROJECT_HEALTH_ALLOW_OFFLINE_FALLBACK", "false").lower() == "true"

    def enrich(self, workbook: ProjectWorkbook, result: RagResult) -> RagResult:
        packet = build_evidence_packet(workbook, result)

        # 1. Groq — Llama 3.3 70B, FREE primary provider
        if self.provider == "groq" and os.getenv("GROQ_API_KEY"):
            payload = self._call_groq(packet)
            if payload:
                return merge_agent_payload(result, payload, MODE_GROQ)
            return self._handle_llm_failure(workbook, result, "groq")

        # 2. Gemini — FREE secondary provider
        if self.provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            payload = self._call_gemini(packet)
            if payload:
                return merge_agent_payload(result, payload, MODE_GEMINI)
            return self._handle_llm_failure(workbook, result, "gemini")

        # 3. OpenAI
        if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
            payload = self._call_openai(packet)
            if payload:
                return merge_agent_payload(result, payload, MODE_OPENAI)
            return self._handle_llm_failure(workbook, result, "openai")

        # 4. Anthropic
        if self.provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            payload = self._call_anthropic(packet)
            if payload:
                return merge_agent_payload(result, payload, MODE_ANTHROPIC)
            return self._handle_llm_failure(workbook, result, "anthropic")

        # No provider configured at all → offline (this is expected when no key is set)
        if self.provider in ("offline", ""):
            return offline_enrichment(workbook, result)

        # Provider configured but key missing — mark failed, do NOT silently go offline
        return self._handle_llm_failure(workbook, result, self.provider)

    def _handle_llm_failure(self, workbook: ProjectWorkbook, result: RagResult, provider: str) -> RagResult:
        """
        Called when an LLM provider is configured but the call fails.
        By default: marks mode as llm_failed, does NOT silently fall back.
        Only falls back to offline if PROJECT_HEALTH_ALLOW_OFFLINE_FALLBACK=true.
        """
        if self.allow_offline_fallback:
            return offline_enrichment(workbook, result)
        # Mark failure but preserve the deterministic result intact
        result.agent_mode = MODE_FAILED
        result.executive_summary = (
            f"[LLM agent call to {provider} failed — check your API key and quota. "
            "Re-run with a valid key to get AI-generated reasoning.]"
        )
        result.sentiment_summary = None
        result.risk_themes = []
        return result

    # ── Groq (OpenAI-compatible) ──────────────────────────────────────────────
    def _call_groq(self, packet: dict[str, Any]) -> dict[str, Any] | None:
        body = {
            "model": self.model or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": _agent_user_prompt(packet)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
            "User-Agent": "ProjectHealthAgent/1.0",
        }
        return _post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            body, headers,
            ("choices", 0, "message", "content"),
        )

    # ── Gemini REST (FREE via Google AI Studio) ───────────────────────────────
    def _call_gemini(self, packet: dict[str, Any]) -> dict[str, Any] | None:
        api_key = os.environ["GEMINI_API_KEY"]
        model = self.model or "gemini-1.5-flash"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
            f":generateContent?key={api_key}"
        )
        body = {
            "system_instruction": {"parts": [{"text": AGENT_SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": _agent_user_prompt(packet)}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        }
        raw = _post_json_raw(url, body, {"Content-Type": "application/json"})
        if raw is None:
            return None
        try:
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            return None

    # ── OpenAI ────────────────────────────────────────────────────────────────
    def _call_openai(self, packet: dict[str, Any]) -> dict[str, Any] | None:
        body = {
            "model": self.model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": _agent_user_prompt(packet)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        }
        return _post_json(
            "https://api.openai.com/v1/chat/completions",
            body, headers,
            ("choices", 0, "message", "content"),
        )

    # ── Anthropic ─────────────────────────────────────────────────────────────
    def _call_anthropic(self, packet: dict[str, Any]) -> dict[str, Any] | None:
        body = {
            "model": self.model or "claude-3-5-sonnet-latest",
            "max_tokens": 1600,
            "temperature": 0.2,
            "system": AGENT_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": _agent_user_prompt(packet)}],
        }
        headers = {
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        return _post_json(
            "https://api.anthropic.com/v1/messages",
            body, headers,
            ("content", 0, "text"),
        )


# ── Evidence packet ────────────────────────────────────────────────────────────

def build_evidence_packet(workbook: ProjectWorkbook, result: RagResult) -> dict[str, Any]:
    metrics = project_metrics(workbook)
    return {
        "project": {
            "name": workbook.detected_project_name,
            "source_file": workbook.source_file,
            "task_sheet": workbook.task_sheet,
            "summary": workbook.summary,
        },
        "deterministic_rag": {
            "status": result.status,
            "score": result.score,
            "confidence": result.confidence,
            "data_quality_score": result.data_quality_score,
            "source_schedule_health": result.source_schedule_health,
            "signals": [asdict(signal) for signal in result.signals],
            "current_reasons": result.reasons,
            "top_risks": result.top_risks,
            "recommendations": result.recommendations,
            "caveats": result.caveats,
        },
        "metrics": metrics,
        "evidence_tasks": _evidence_tasks(workbook),
        "comments": [
            {
                "source_row": c.source_row,
                "referenced_row": c.referenced_row,
                "author": c.author,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "comment_text": c.comment_text,
            }
            for c in workbook.comments[:30]
        ],
        "data_quality_issues": [asdict(i) for i in workbook.data_quality_issues[:20]],
        "agent_rules": {
            "must_not_change_rag_status": True,
            "must_cite_source_row_numbers": True,
            "budget_unavailable_if_columns_absent": True,
            "sentiment_unavailable_if_no_comments": True,
        },
    }


def merge_agent_payload(result: RagResult, payload: dict[str, Any], mode: str) -> RagResult:
    result.agent_mode = mode
    result.executive_summary = _text(payload.get("executive_summary"))
    result.sentiment_summary = _text(payload.get("sentiment_summary"))
    result.risk_themes = _list(payload.get("risk_themes"))[:6]
    if reasons := _list(payload.get("reasons")):
        result.reasons = reasons[:6]
    if risks := _list(payload.get("top_risks")):
        result.top_risks = risks[:8]
    if recs := _list(payload.get("recommendations")):
        result.recommendations = recs[:6]
    if caveats := _list(payload.get("data_caveats")):
        result.caveats = list(dict.fromkeys(result.caveats + caveats))[:8]
    return result


def offline_enrichment(workbook: ProjectWorkbook, result: RagResult) -> RagResult:
    """
    Deterministic fallback — used ONLY when provider=offline or
    PROJECT_HEALTH_ALLOW_OFFLINE_FALLBACK=true.
    Produces structured, evidence-citing summaries from computed signals.
    """
    project_stage = workbook.summary.get("Project Stage")
    project_name = workbook.detected_project_name

    top_signals = sorted(
        [s for s in result.signals if s.score >= 0],
        key=lambda s: s.weighted_score, reverse=True,
    )
    parts = [
        f"{project_name} is rated {result.status} "
        f"(score {result.score}/100, {result.confidence.lower()} confidence)."
    ]
    if project_stage:
        parts.append(f"The project is currently in {project_stage}.")
    if top_signals:
        p = top_signals[0]
        cite = p.evidence[0] if p.evidence else p.raw_value
        parts.append(f"The dominant risk driver is {p.name}: {cite}.")
    if len(top_signals) > 1:
        s = top_signals[1]
        cite2 = s.evidence[0] if s.evidence else s.raw_value
        parts.append(f"A secondary concern is {s.name}: {cite2}.")
    if result.source_schedule_health:
        parts.append(f"Workbook source schedule health: {result.source_schedule_health}.")
    result.executive_summary = " ".join(parts)

    if workbook.comments:
        neg_kw = ["pending", "delay", "impacted", "remain", "need", "mapping",
                  "blocked", "risk", "issue", "overdue"]
        pos_kw = ["completed", "done", "resolved", "on track", "achieved"]
        neg = [c for c in workbook.comments if any(w in c.comment_text.lower() for w in neg_kw)]
        pos = [c for c in workbook.comments if any(w in c.comment_text.lower() for w in pos_kw)]
        total = len(workbook.comments)
        if neg:
            s = neg[0]
            by = f" ({s.author})" if s.author else ""
            result.sentiment_summary = (
                f"{len(neg)} of {total} comments show delivery friction. "
                f"Row {s.source_row}{by}: \"{s.comment_text[:160]}\""
            )
            if len(neg) > 1:
                result.sentiment_summary += f" and {len(neg)-1} more similar."
        elif pos:
            result.sentiment_summary = f"Comments predominantly positive ({len(pos)}/{total}). No blocker language."
        else:
            result.sentiment_summary = f"{total} comments: no strong positive or negative signals detected."
    else:
        result.sentiment_summary = "No stakeholder comments — sentiment unavailable."

    result.risk_themes = _offline_risk_themes(workbook)
    if result.reasons:
        result.reasons[0] = result.executive_summary
    else:
        result.reasons.append(result.executive_summary)

    lead = {
        "Red": "Escalate to executive attention. Assign named owners to the top schedule and dependency risks before the next weekly review.",
        "Amber": "Place in weekly watch mode. Resolve the largest risk contributor before it becomes a client escalation.",
        "Green": "Maintain current delivery cadence and continue tracking leading indicators weekly.",
    }.get(result.status, "Review project status with the PM.")
    result.recommendations.insert(0, lead)
    result.recommendations = list(dict.fromkeys(result.recommendations))[:6]
    result.agent_mode = MODE_OFFLINE
    return result


# ── Prompt ────────────────────────────────────────────────────────────────────

def _agent_user_prompt(packet: dict[str, Any]) -> str:
    status = packet["deterministic_rag"]["status"]
    return (
        f"Analyse this project evidence packet. The RAG status is {status} and must NOT be changed.\n"
        "Return a JSON object with exactly these keys:\n"
        "  executive_summary  — 2-4 sentences citing the top signal evidence and source_row numbers\n"
        "  sentiment_summary  — 1-3 sentences citing comment source_rows; 'No comments available' if empty\n"
        "  risk_themes        — array of 3-5 short strings naming emerging risk patterns\n"
        "  reasons            — array of 3-5 strings explaining why the status is what it is\n"
        "  top_risks          — array of up to 6 specific task-level risks with source_row\n"
        "  recommendations    — array of 4-6 actionable steps for leadership\n"
        "  data_caveats       — array of honest notes about missing/low-quality data\n\n"
        f"{json.dumps(packet, default=str)}"
    )


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _post_json_raw(url: str, body: dict, headers: dict) -> dict | None:
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _post_json(url: str, body: dict, headers: dict, path: tuple) -> dict | None:
    raw = _post_json_raw(url, body, headers)
    if raw is None:
        return None
    node: Any = raw
    try:
        for key in path:
            node = node[key]
        return json.loads(node)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return None


# ── Task evidence ──────────────────────────────────────────────────────────────

def _evidence_tasks(workbook: ProjectWorkbook) -> list[dict]:
    risky = []
    for task in workbook.tasks:
        text = " ".join([task.status_comment or "", task.comments or "", task.task_name or ""]).lower()
        health = (task.source_schedule_health or "").lower()
        active = (task.status or "").lower() not in {"completed", "complete"}
        blocker_kw = ["pending", "delay", "impacted", "remain", "mapping"]
        if (
            health in {"red", "yellow", "amber"}
            or (task.critical and active)
            or task.on_hold
            or (task.total_float is not None and task.total_float < 0)
            or any(w in text for w in blocker_kw)
        ):
            risky.append({
                "source_row": task.source_row,
                "parent_source_row": task.parent_source_row,
                "level": task.level,
                "task_name": task.task_name,
                "phase_milestone": task.phase_milestone,
                "status": task.status,
                "percent_complete": task.percent_complete,
                "source_schedule_health": task.source_schedule_health,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "baseline_start": task.baseline_start.isoformat() if task.baseline_start else None,
                "baseline_finish": task.baseline_finish.isoformat() if task.baseline_finish else None,
                "variance": task.variance,
                "total_float": task.total_float,
                "critical": task.critical,
                "on_hold": task.on_hold,
                "owner": task.owner,
                "assigned_to": task.assigned_to,
                "status_comment": task.status_comment,
            })
    return risky[:30]


def _offline_risk_themes(workbook: ProjectWorkbook) -> list[str]:
    text = "\n".join(
        [c.comment_text for c in workbook.comments]
        + [t.status_comment or "" for t in workbook.tasks]
    ).lower()
    themes = []
    if any(w in text for w in ["mapping", "jde", "integration"]):
        themes.append("Integration or field-mapping dependency")
    if any(w in text for w in ["workshop", "agenda", "session"]):
        themes.append("Workshop/session schedule coordination")
    if any(w in text for w in ["pending", "remain", "need", "waiting"]):
        themes.append("Open owner follow-up or pending action")
    if any(w in text for w in ["critical", "float", "delay", "slip"]):
        themes.append("Critical-path schedule slippage")
    if not themes:
        themes.append("No repeated risk theme detected from available data")
    return themes


# ── Provider detection ─────────────────────────────────────────────────────────

def _detect_provider() -> str:
    """Auto-detect provider from available keys. Groq wins (free + powerful)."""
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "offline"


def _default_model(provider: str) -> str:
    return {
        "groq": "llama-3.3-70b-versatile",
        "gemini": "gemini-1.5-flash",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-sonnet-latest",
    }.get(provider, "offline")


# ── Utilities ──────────────────────────────────────────────────────────────────

def _text(value: Any) -> str | None:
    if value is None:
        return None
    t = str(value).strip()
    return t or None


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(i).strip() for i in value if str(i).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []
