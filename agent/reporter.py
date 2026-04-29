from datetime import datetime, date
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def _debate_block(d: dict) -> str:
    return f"""### {d['topic']}

**Insight (Llama):** {d['insight']}

**Counterpoint (Gemini):** {d['counterpoint']}

**Rebuttal (Llama):** {d['rebuttal']}

**Synthesis:** {d['synthesis']}

---
"""


def generate_daily_report(debates: list[dict], articles: list[dict]) -> Path:
    today = date.today().isoformat()
    path = REPORTS_DIR / "daily" / f"{today}.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    domain_map: dict[str, list] = {}
    for a in articles:
        domain_map.setdefault(a["domain"], []).append(a)

    lines = [f"# Daily Report — {today}\n"]

    for domain, items in domain_map.items():
        label = {"ai_tech": "AI & Tech", "creative": "Creative", "self_determined": "Self-Determined"}.get(domain, domain)
        lines.append(f"## {label}\n")
        for item in items:
            lines.append(f"- [{item['title']}]({item['link']})")
        lines.append("")

    lines.append("## Debates & Synthesis\n")
    for d in debates:
        lines.append(_debate_block(d))

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[reporter] Daily report saved: {path}")
    return path


def generate_weekly_report(debates: list[dict], articles: list[dict], self_log: dict) -> Path:
    today = datetime.today()
    week_num = today.isocalendar()[1]
    year = today.year
    path = REPORTS_DIR / "weekly" / f"{year}-W{week_num:02d}.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    recent_runs = self_log.get("runs", [])[-7:]
    past_topics = [t for run in recent_runs for t in run.get("topics", [])]

    lines = [
        f"# Weekly Report — {year} Week {week_num}\n",
        f"**Topics covered this week:** {', '.join(past_topics) if past_topics else 'First run'}\n",
        "## This Week's Debates\n",
    ]
    for d in debates:
        lines.append(_debate_block(d))

    learned = self_log.get("keywords", {}).get("self_determined", [])
    lines.append("## Self-Learning Log\n")
    lines.append(f"**Auto-discovered keywords:** {', '.join(learned) if learned else 'None yet'}\n")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[reporter] Weekly report saved: {path}")
    return path
