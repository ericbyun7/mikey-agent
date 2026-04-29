import sys
import json
import argparse
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from collector import collect_all
from debate import run_debate
from reporter import generate_daily_report, generate_weekly_report
from mailer import send_report_email
from dashboard import generate_dashboard

LOG_PATH = Path(__file__).parent / "self_log.json"


def load_log() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {"runs": [], "keywords": {"ai_tech": [], "creative": [], "self_determined": []}, "topic_scores": {}}


def _extract_new_keywords(debates: list[dict]) -> list[str]:
    words = set()
    for d in debates:
        for text in [d.get("synthesis", ""), d.get("insight", "")]:
            for word in text.split():
                word = word.strip(".,;:()[]\"'").lower()
                if len(word) > 5 and word.isalpha():
                    words.add(word)
    stopwords = {"about", "after", "their", "which", "while", "would", "could", "should", "where", "these", "those", "there", "being", "because", "through", "however", "although"}
    return [w for w in words if w not in stopwords][:10]


def save_log(self_log: dict, debates: list[dict], articles: list[dict]) -> None:
    new_keywords = _extract_new_keywords(debates)
    existing = set(self_log["keywords"].get("self_determined", []))
    merged = list(existing | set(new_keywords))[:20]
    self_log["keywords"]["self_determined"] = merged

    for d in debates:
        score = len(d.get("synthesis", ""))
        self_log["topic_scores"][d["topic"][:80]] = score

    self_log["runs"].append({
        "date": datetime.utcnow().isoformat(),
        "articles_collected": len(articles),
        "debates_run": len(debates),
        "topics": [d["topic"][:80] for d in debates],
        "new_keywords": new_keywords,
    })

    self_log["runs"] = self_log["runs"][-30:]
    LOG_PATH.write_text(json.dumps(self_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[main] Self-log updated ({len(self_log['runs'])} runs recorded)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily", "weekly"], default="daily")
    args = parser.parse_args()

    custom_topic = os.environ.get("CUSTOM_TOPIC", "").strip()
    if custom_topic:
        print(f"[main] Custom topic override: {custom_topic}")

    print(f"[main] Starting {args.mode} run...")

    self_log = load_log()

    articles = collect_all(self_log)
    print(f"[main] Collected {len(articles)} articles")

    if not articles:
        print("[main] No articles found — exiting")
        return

    debate_targets = articles[:3]
    if custom_topic:
        debate_targets = [{"title": custom_topic, "summary": custom_topic, "link": "", "domain": "custom"}] + debate_targets[:2]

    debates = []
    for article in debate_targets:
        print(f"[main] Debating: {article['title'][:60]}...")
        result = run_debate(article["title"], article["summary"])
        debates.append(result)

    if args.mode == "daily":
        report_path = generate_daily_report(debates, articles)
    else:
        report_path = generate_weekly_report(debates, articles, self_log)

    generate_dashboard()
    send_report_email(report_path, args.mode)
    save_log(self_log, debates, articles)

    print(f"[main] Done. Report: {report_path}")


if __name__ == "__main__":
    main()
