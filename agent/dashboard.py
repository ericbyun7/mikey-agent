from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(__file__).parent.parent / "reports"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def _card(title: str, link: str, preview: str) -> str:
    return f"""
    <div class="card">
      <a href="{link}"><h3>{title}</h3></a>
      <p>{preview}</p>
    </div>"""


def _read_preview(path: Path) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        synthesis = next((l.replace("**Synthesis:**", "").strip() for l in lines if "**Synthesis:**" in l), "")
        return synthesis[:200] + "..." if len(synthesis) > 200 else synthesis
    except Exception:
        return ""


def generate_dashboard() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    daily_reports = sorted((REPORTS_DIR / "daily").glob("*.md"), reverse=True)
    weekly_reports = sorted((REPORTS_DIR / "weekly").glob("*.md"), reverse=True)

    daily_cards = "".join(
        _card(p.stem, f"daily/{p.name}", _read_preview(p))
        for p in daily_reports[:10]
    )
    weekly_cards = "".join(
        _card(p.stem, f"weekly/{p.name}", _read_preview(p))
        for p in weekly_reports[:5]
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mikey Agent Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; background: #0f0f0f; color: #e0e0e0; }}
    h1 {{ color: #a78bfa; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
    h2 {{ color: #7dd3fc; margin-top: 2rem; }}
    .card {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 1rem 1.5rem; margin-bottom: 1rem; }}
    .card a {{ color: #a78bfa; text-decoration: none; }}
    .card a:hover {{ text-decoration: underline; }}
    .card p {{ color: #9ca3af; font-size: 0.9rem; margin: 0.5rem 0 0; }}
    .updated {{ color: #4b5563; font-size: 0.8rem; margin-top: 3rem; }}
  </style>
</head>
<body>
  <h1>Mikey Agent</h1>
  <p>자율 AI 에이전트 — 매일 정보 수집, 토론, 자가계발</p>

  <h2>Daily Reports</h2>
  {daily_cards if daily_cards else '<p>아직 리포트가 없어. 첫 실행 후 여기에 나타나!</p>'}

  <h2>Weekly Synthesis</h2>
  {weekly_cards if weekly_cards else '<p>아직 주간 리포트가 없어.</p>'}

  <p class="updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
</body>
</html>"""

    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print("[dashboard] index.html generated")
