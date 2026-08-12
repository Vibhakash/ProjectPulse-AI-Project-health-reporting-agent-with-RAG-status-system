"""
Email alert service for RAG status flip notifications.
Sends HTML email when a project's RAG status changes (e.g. Green -> Red).
Gracefully no-ops if SMTP environment variables are not configured.
"""
from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


# ── RAG color mapping for email HTML ──────────────────────────────────────────
_RAG_COLORS = {
    "Red":   ("#DC2626", "#FEF2F2"),
    "Amber": ("#D97706", "#FFFBEB"),
    "Green": ("#16A34A", "#F0FDF4"),
}

_SEVERITY_LABELS = {
    ("Green", "Amber"): "Watch-List Alert",
    ("Amber", "Red"):   "CRITICAL ESCALATION",
    ("Green", "Red"):   "CRITICAL ESCALATION",
    ("Red", "Amber"):   "Recovery Notice",
    ("Amber", "Green"): "Recovery Notice",
    ("Red", "Green"):   "Full Recovery Notice",
}


def send_rag_flip_alert(
    project_name: str,
    old_status: str,
    new_status: str,
    run_date: str | None = None,
    to_email: str | None = None,
) -> bool:
    """
    Send an HTML email alert when a project's RAG status changes.

    Returns True if email was sent, False if skipped (no config) or failed.
    Required .env vars:
      ALERT_SMTP_HOST, ALERT_SMTP_PORT, ALERT_SMTP_USER, ALERT_SMTP_PASS
      ALERT_EMAIL_TO  (comma-separated list of recipient emails)
    """
    smtp_host = os.getenv("ALERT_SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("ALERT_SMTP_PORT", "587"))
    smtp_user = os.getenv("ALERT_SMTP_USER", "").strip()
    smtp_pass = os.getenv("ALERT_SMTP_PASS", "").strip()
    email_to  = (to_email or os.getenv("ALERT_EMAIL_TO", "")).strip()

    # If any SMTP config is missing, silently skip
    if not all([smtp_host, smtp_user, smtp_pass, email_to]):
        return False

    # Compose message
    recipients = [e.strip() for e in email_to.split(",") if e.strip()]
    if not recipients:
        return False

    severity = _SEVERITY_LABELS.get((old_status, new_status), "RAG Status Change")
    old_color, old_bg = _RAG_COLORS.get(old_status, ("#6B7280", "#F9FAFB"))
    new_color, new_bg = _RAG_COLORS.get(new_status, ("#6B7280", "#F9FAFB"))
    ts = run_date or datetime.now().strftime("%Y-%m-%d")

    subject = f"[ProjectPulse AI] {severity}: {project_name} - {old_status} -> {new_status}"

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
        <!-- Header -->
        <tr>
          <td style="background:#1E3A5F;padding:28px 32px;">
            <h1 style="margin:0;color:#FFFFFF;font-size:20px;font-weight:700;">ProjectPulse AI</h1>
            <p style="margin:4px 0 0;color:#94A3B8;font-size:13px;">Automated Project Health Alert</p>
          </td>
        </tr>
        <!-- Severity badge -->
        <tr>
          <td style="background:{new_bg};padding:20px 32px;border-bottom:3px solid {new_color};">
            <p style="margin:0;font-size:13px;color:#6B7280;text-transform:uppercase;letter-spacing:1px;font-weight:600;">{severity}</p>
            <h2 style="margin:6px 0 0;font-size:24px;color:{new_color};font-weight:800;">{project_name}</h2>
            <p style="margin:4px 0 0;font-size:13px;color:#6B7280;">Detected on {ts}</p>
          </td>
        </tr>
        <!-- Status change -->
        <tr>
          <td style="padding:32px;">
            <p style="margin:0 0 20px;font-size:15px;color:#374151;">The RAG health status for <strong>{project_name}</strong> has changed:</p>
            <table cellpadding="0" cellspacing="0" style="margin:0 auto 24px;">
              <tr>
                <td style="background:{old_bg};border:2px solid {old_color};border-radius:8px;padding:16px 28px;text-align:center;">
                  <p style="margin:0;font-size:12px;color:{old_color};font-weight:600;text-transform:uppercase;">Previous</p>
                  <p style="margin:4px 0 0;font-size:28px;font-weight:900;color:{old_color};">{old_status}</p>
                </td>
                <td style="padding:0 20px;font-size:28px;color:#9CA3AF;">-&gt;</td>
                <td style="background:{new_bg};border:2px solid {new_color};border-radius:8px;padding:16px 28px;text-align:center;">
                  <p style="margin:0;font-size:12px;color:{new_color};font-weight:600;text-transform:uppercase;">Current</p>
                  <p style="margin:4px 0 0;font-size:28px;font-weight:900;color:{new_color};">{new_status}</p>
                </td>
              </tr>
            </table>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;"><strong>Recommended action:</strong></p>
            <p style="margin:0;font-size:14px;color:#6B7280;line-height:1.6;">{_get_recommendation(new_status)}</p>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#F8FAFC;padding:16px 32px;border-top:1px solid #E2E8F0;">
            <p style="margin:0;font-size:11px;color:#9CA3AF;">Generated by ProjectPulse AI Automated Agent · This is an automated alert. Please log in to the dashboard for full details.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.sendmail(smtp_user, recipients, msg.as_string())
        print(f"[AlertService] Email sent: {subject}")
        return True
    except Exception as exc:
        print(f"[AlertService] Email failed (continuing without alert): {exc}")
        return False


def _get_recommendation(new_status: str) -> str:
    return {
        "Red":   "Immediate executive attention required. Schedule an escalation call and assign named owners to the top risks before the next review cycle.",
        "Amber": "Place this project on the weekly watch list. Resolve the largest risk signal before it escalates further.",
        "Green": "Project has recovered to healthy status. Continue monitoring leading indicators weekly.",
    }.get(new_status, "Review the project dashboard for full context.")
