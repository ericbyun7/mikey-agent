import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

RECIPIENT = "eric.byun7@gmail.com"
PAGES_BASE = "https://{username}.github.io/mikey-agent"


def send_report_email(report_path: Path, mode: str) -> None:
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_password:
        print("[mailer] Gmail credentials not set — skipping email")
        return

    content = report_path.read_text(encoding="utf-8")
    lines = [l for l in content.splitlines() if l.strip()]

    summary_lines = []
    for line in lines:
        if line.startswith("**종합 결론:**"):
            summary_lines.append(line.replace("**종합 결론:**", "").strip())
        if len(summary_lines) >= 3:
            break

    mode_label = "일일" if mode == "daily" else "주간"
    subject = f"[Mikey Agent] {mode_label} 리포트 — {report_path.stem}"
    body = "\n\n".join([
        f"Mikey Agent {mode_label} 리포트",
        "--- 오늘의 핵심 인사이트 ---",
        "\n".join(f"{i+1}. {s}" for i, s in enumerate(summary_lines)) or "종합 결론이 없습니다.",
        f"전체 리포트: {report_path.name}",
    ])

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, RECIPIENT, msg.as_string())
        print(f"[mailer] Email sent to {RECIPIENT}")
    except Exception as e:
        print(f"[mailer] Failed to send email: {e}")
