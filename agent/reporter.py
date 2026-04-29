from datetime import datetime, date
from pathlib import Path

REPORTS_DIR = Path(__file__).parent.parent / "reports"

DOMAIN_LABELS = {
    "ai_tech": "AI & Tech 동향",
    "creative": "크리에이티브",
    "self_determined": "자기학습 인사이트",
    "custom": "커스텀 주제",
}


def _korean_date(d: date) -> str:
    return f"{d.year}년 {d.month:02d}월 {d.day:02d}일"


def _debate_block(d: dict) -> str:
    return f"""### {d['topic']}

**인사이트 (Llama):** {d['insight']}

**반론 (Gemini):** {d['counterpoint']}

**재반박 (Llama):** {d['rebuttal']}

**종합 결론:** {d['synthesis']}

---
"""


def generate_daily_report(debates: list[dict], articles: list[dict]) -> Path:
    today = date.today()
    path = REPORTS_DIR / "daily" / f"{today.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    domain_map: dict[str, list] = {}
    for a in articles:
        domain_map.setdefault(a["domain"], []).append(a)

    lines = [f"# {_korean_date(today)} 일일 리포트\n"]

    for domain, items in domain_map.items():
        label = DOMAIN_LABELS.get(domain, domain)
        lines.append(f"## {label}\n")
        for item in items:
            lines.append(f"- [{item['title']}]({item['link']})")
        lines.append("")

    lines.append("## 토론 및 종합 결론\n")
    for d in debates:
        lines.append(_debate_block(d))

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[reporter] 일일 리포트 저장: {path}")
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
        f"# {year}년 {week_num}주차 주간 리포트\n",
        f"**이번 주 다룬 주제:** {', '.join(past_topics) if past_topics else '첫 번째 실행'}\n",
        "## 이번 주 토론 결과\n",
    ]
    for d in debates:
        lines.append(_debate_block(d))

    learned = self_log.get("keywords", {}).get("self_determined", [])
    lines.append("## 자기학습 로그\n")
    lines.append(f"**자동 발견 키워드:** {', '.join(learned) if learned else '아직 없음'}\n")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[reporter] 주간 리포트 저장: {path}")
    return path
