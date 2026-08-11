"""
PDF report generator for individual project snapshots.
Uses reportlab to produce a highly structured, premium PDF from snapshot data.
"""
from __future__ import annotations

import io
import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any


def generate_snapshot_pdf(conn: sqlite3.Connection, snapshot_id: int) -> bytes:
    """
    Generate a styled PDF for a single project snapshot.
    Returns the raw PDF bytes.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            KeepTogether, Image
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    except ImportError:
        raise RuntimeError("reportlab is not installed. Run: pip install reportlab")

    # ── Fetch snapshot data ──────────────────────────────────────────────────
    snap_row = conn.execute(
        """
        SELECT ps.*, p.name AS project_name, p.source_file, p.project_manager
        FROM project_snapshots ps
        JOIN projects p ON p.id = ps.project_id
        WHERE ps.id = ?
        """,
        (snapshot_id,),
    ).fetchone()

    if not snap_row:
        raise ValueError(f"Snapshot {snapshot_id} not found")

    snap = dict(snap_row)

    # Load signals
    sig_rows = conn.execute(
        """
        SELECT signal_name, weight, raw_value, score, weighted_score, triggered_override
        FROM rag_signals WHERE snapshot_id = ? ORDER BY weighted_score DESC
        """,
        (snapshot_id,),
    ).fetchall()
    signals = [dict(r) for r in sig_rows]

    # Load agent fields
    agent_data = _load_agent_fields(snap)

    # ── Color Palette (Premium Indigo & Slate) ───────────────────────────────
    C_BRAND   = colors.HexColor("#0F172A")  # Slate 900
    C_ACCENT  = colors.HexColor("#4F46E5")  # Indigo 600
    C_TEXT    = colors.HexColor("#334155")  # Slate 700
    C_LIGHT   = colors.HexColor("#F8FAFC")  # Slate 50
    C_BORDER  = colors.HexColor("#E2E8F0")  # Slate 200
    C_WHITE   = colors.white
    
    C_RED     = colors.HexColor("#DC2626")
    C_RED_BG  = colors.HexColor("#FEF2F2")
    C_AMBER   = colors.HexColor("#D97706")
    C_AMB_BG  = colors.HexColor("#FFFBEB")
    C_GREEN   = colors.HexColor("#16A34A")
    C_GRN_BG  = colors.HexColor("#F0FDF4")

    def rag_color(status):
        return {"Red": C_RED, "Amber": C_AMBER, "Green": C_GREEN}.get(status, C_TEXT)

    def rag_bg(status):
        return {"Red": C_RED_BG, "Amber": C_AMB_BG, "Green": C_GRN_BG}.get(status, C_LIGHT)

    # ── Styles ───────────────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    def style(name, **kwargs):
        kwargs.setdefault("fontName", "Helvetica")
        if "fontSize" in kwargs and "leading" not in kwargs:
            kwargs["leading"] = kwargs["fontSize"] * 1.25
        return ParagraphStyle(name, parent=base["Normal"], **kwargs)

    TITLE = style("TITLE", fontSize=24, fontName="Helvetica-Bold", textColor=C_BRAND, spaceAfter=6)
    SUBTITLE = style("SUBTITLE", fontSize=10, textColor=C_TEXT, spaceAfter=15)
    
    H2 = style("H2", fontSize=14, fontName="Helvetica-Bold", textColor=C_BRAND, spaceBefore=15, spaceAfter=8)
    H3 = style("H3", fontSize=11, fontName="Helvetica-Bold", textColor=C_ACCENT, spaceBefore=8, spaceAfter=4)
    
    BODY = style("BODY", fontSize=9, leading=14, textColor=C_TEXT)
    BODY_BOLD = style("BODY_BOLD", fontSize=9, fontName="Helvetica-Bold", textColor=C_BRAND)
    
    METRIC_VAL = style("METRIC_VAL", fontSize=16, fontName="Helvetica-Bold", textColor=C_BRAND)
    METRIC_LBL = style("METRIC_LBL", fontSize=8, textColor=colors.HexColor("#64748B"), spaceAfter=2)
    
    RAG_HUGE = style("RAG_HUGE", fontSize=26, fontName="Helvetica-Bold", textColor=rag_color(snap["rag_status"]), alignment=TA_CENTER)
    
    BULLET = style("BULLET", fontSize=9, leading=14, textColor=C_TEXT, leftIndent=10, firstLineIndent=-10)

    # ── Build Document ───────────────────────────────────────────────────────
    buffer = io.BytesIO()
    margin = 15 * mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
    )
    W = A4[0] - 2 * margin
    story = []

    # ── Header Section ───────────────────────────────────────────────────────
    story.append(Paragraph(snap["project_name"].upper(), TITLE))
    meta_text = (
        f"<b>Snapshot:</b> #{snapshot_id} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Run Date:</b> {snap['run_date']} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>PM:</b> {snap.get('project_manager') or 'N/A'}"
    )
    story.append(Paragraph(meta_text, SUBTITLE))
    
    # ── Executive Summary & RAG Dashboard (Two Column Table) ─────────────────
    rag_status = snap["rag_status"]
    exec_text = agent_data.get("executive_summary", "No executive summary generated.")
    
    # Left Column: RAG Badge & Metrics
    metrics_data = [
        [Paragraph("Score", METRIC_LBL), Paragraph("Confidence", METRIC_LBL)],
        [Paragraph(f"{snap['rag_score']:.1f}", METRIC_VAL), Paragraph(snap["confidence"], METRIC_VAL)],
        [Paragraph("Data Quality", METRIC_LBL), Paragraph("Schedule", METRIC_LBL)],
        [Paragraph(f"{snap['data_quality_score']:.1f}%", METRIC_VAL), Paragraph(snap.get("source_schedule_health") or "N/A", METRIC_VAL)]
    ]
    metrics_table = Table(metrics_data, colWidths=[W*0.15, W*0.15])
    metrics_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,1), (-1,1), 10),
    ]))
    
    left_col = [
        Spacer(1, 10),
        Paragraph(rag_status.upper(), RAG_HUGE),
        Spacer(1, 15),
        metrics_table
    ]
    
    # Right Column: Exec Summary
    right_col = [
        Paragraph("EXECUTIVE SUMMARY", style("ES_TITLE", fontSize=10, fontName="Helvetica-Bold", textColor=C_ACCENT, spaceAfter=8)),
        Paragraph(exec_text, style("ES_BODY", fontSize=9.5, leading=15, textColor=C_BRAND, alignment=TA_JUSTIFY))
    ]
    
    dash_table = Table([[left_col, right_col]], colWidths=[W*0.35, W*0.65])
    dash_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), rag_bg(rag_status)),
        ("BACKGROUND", (1,0), (1,0), C_LIGHT),
        ("BOX", (0,0), (-1,-1), 1, C_BORDER),
        ("INNERGRID", (0,0), (-1,-1), 1, C_BORDER),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("PADDING", (0,0), (-1,-1), 15),
    ]))
    story.append(dash_table)
    story.append(Spacer(1, 15))

    # ── Insights Section (Risks, Reasons, Recs) ──────────────────────────────
    def make_list_card(title, items, color_hex):
        if not items: return None
        content = [Paragraph(title.upper(), style("CARD_TITLE", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor(color_hex), spaceAfter=8))]
        for item in items[:5]:
            content.append(Paragraph(f"• {_clean_risk(item)}", BULLET))
        
        t = Table([[content]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), C_WHITE),
            ("BOX", (0,0), (0,0), 1, C_BORDER),
            ("LINEBEFORE", (0,0), (0,0), 4, colors.HexColor(color_hex)),
            ("PADDING", (0,0), (0,0), 12),
        ]))
        return t

    reasons = agent_data.get("reasons", [])
    risks = agent_data.get("top_risks", [])
    recs = agent_data.get("recommendations", [])
    
    if reasons or risks or recs:
        story.append(Paragraph("AI Agent Insights", H2))
        
        if risks:
            story.append(make_list_card("Top Risks", risks, "#DC2626"))
            story.append(Spacer(1, 10))
            
        if reasons:
            story.append(make_list_card("Key Drivers", reasons, "#4F46E5"))
            story.append(Spacer(1, 10))
            
        if recs:
            story.append(make_list_card("Recommendations", recs, "#059669"))
            story.append(Spacer(1, 15))

    # ── Signal Breakdown ─────────────────────────────────────────────────────
    if signals:
        story.append(KeepTogether([
            Paragraph("Signal Breakdown", H2),
            _build_signal_table(signals, W, BODY, C_BRAND, C_LIGHT, C_BORDER, C_WHITE, C_RED)
        ]))
        story.append(Spacer(1, 15))

    # ── Stakeholder Sentiment ────────────────────────────────────────────────
    sent = agent_data.get("sentiment_summary")
    if sent:
        story.append(KeepTogether([
            Paragraph("Stakeholder Sentiment", H2),
            Paragraph(sent, BODY)
        ]))

    # ── Generate ─────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return buffer.getvalue()


def _build_signal_table(signals, W, BODY_STYLE, C_BRAND, C_LIGHT, C_BORDER, C_WHITE, C_RED):
    from reportlab.platypus import Table, TableStyle, Paragraph
    
    data = [["Signal", "Weight", "Score", "Impact", "Override"]]
    for s in signals:
        override = "YES" if s.get("triggered_override") else "—"
        data.append([
            Paragraph(s["signal_name"], BODY_STYLE),
            f"{s['weight']*100:.0f}%",
            f"{s['score']:.1f}",
            f"{s['weighted_score']:.1f}",
            override,
        ])
        
    t = Table(data, colWidths=[W * 0.45, W * 0.12, W * 0.12, W * 0.15, W * 0.16])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("PADDING", (0, 0), (-1, -1), 8),
    ])
    
    for ri, row in enumerate(data[1:], start=1):
        if row[-1] == "YES":
            style.add("TEXTCOLOR", (4, ri), (4, ri), C_RED)
            style.add("FONTNAME", (4, ri), (4, ri), "Helvetica-Bold")
            
    t.setStyle(style)
    return t


def _header_footer(canvas, doc):
    """Draw branding header and page number footer on every page."""
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    canvas.saveState()
    
    # Top indigo band
    canvas.setFillColor(colors.HexColor("#4F46E5"))
    canvas.rect(0, doc.pagesize[1] - 6 * mm, doc.pagesize[0], 6 * mm, fill=1, stroke=0)
    
    # Bottom subtle border
    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(1)
    canvas.line(15 * mm, 15 * mm, doc.pagesize[0] - 15 * mm, 15 * mm)
    
    # Page number bottom right
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(
        doc.pagesize[0] - 15 * mm,
        10 * mm,
        f"Page {canvas.getPageNumber()}  |  ProjectPulse AI",
    )
    canvas.restoreState()


def _load_agent_fields(snap: dict) -> dict:
    weekly_path = snap.get("weekly_json_path")
    if weekly_path:
        p = Path(weekly_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                rag = data.get("rag", {})
                if rag:
                    return {
                        "executive_summary": rag.get("executive_summary"),
                        "sentiment_summary":  rag.get("sentiment_summary"),
                        "risk_themes":        rag.get("risk_themes", []),
                        "reasons":            rag.get("reasons", []),
                        "top_risks":          rag.get("top_risks", []),
                        "recommendations":    rag.get("recommendations", []),
                        "caveats":            rag.get("data_caveats", []),
                    }
            except Exception:
                pass
                
    summary_raw = snap.get("summary_json")
    if summary_raw:
        try:
            data = json.loads(summary_raw)
            return {
                "reasons":         data.get("reasons", []),
                "top_risks":       data.get("top_risks", []),
                "recommendations": data.get("recommendations", []),
                "caveats":         data.get("caveats", []),
            }
        except Exception:
            pass
    return {}


def _clean_risk(raw: str) -> str:
    if "|" in raw:
        parts = [p.strip() for p in raw.split("|")]
        return " | ".join(parts)
    return str(raw).replace("_", " ")
