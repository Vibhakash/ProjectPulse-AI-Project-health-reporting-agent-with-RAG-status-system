# Project Health Agent Responsibilities

The backend includes an optional Project Health Agent layer on top of the deterministic RAG rule engine.

## Core Principle

The LLM agent must not decide the RAG color.

The RAG status and score are calculated by the transparent rule engine in:

- `src/project_health/rag_engine.py`
- `config/rag_weights.json`

The agent receives the computed signals and evidence, then explains and synthesizes them.

## What The Agent Does

The Project Health Agent:

1. Reads computed RAG output from the deterministic rule engine.
2. Reviews signal evidence for schedule, progress, milestones, blockers, sentiment, and budget availability.
3. Reviews task evidence with source row numbers.
4. Reviews Comments sheet text for stakeholder sentiment.
5. Produces an executive summary.
6. Produces a stakeholder sentiment summary when comments exist.
7. Extracts recurring risk themes.
8. Writes plain-English reasons for the RAG status.
9. Cites specific task rows or comment rows when making claims.
10. Recommends next actions for PMs and leadership.
11. Calls out missing or messy data honestly.

## What The Agent Must Not Do

The agent must not:

- Change the RAG color.
- Change the deterministic RAG score.
- Invent missing comments.
- Invent budget burn when budget fields are absent.
- Invent task owners, dates, milestones, or blockers.
- Hide data quality caveats.
- Produce generic reasoning without row/comment evidence.

## LLM Usage

The agent supports optional LLM enrichment.

Supported providers:

- OpenAI, using `OPENAI_API_KEY`
- Anthropic Claude, using `ANTHROPIC_API_KEY`

Environment variables:

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PROJECT_HEALTH_LLM_PROVIDER=openai
PROJECT_HEALTH_LLM_MODEL=gpt-4o-mini
```

If no API key is configured, the agent runs in offline deterministic mode.

## Why This Design Meets The Assignment

The assignment asks for a clear, explainable RAG framework and plain-English reasoning. A black-box LLM should not make the health decision. This design keeps the decision transparent while using the LLM only where it is strongest:

- summarizing stakeholder comments,
- grouping risk themes,
- improving executive wording,
- producing actionable recommendations from already-computed evidence.

