import feedparser
import requests

RSS_SOURCES = {
    "ai_tech": [
        "http://export.arxiv.org/rss/cs.AI",
        "https://hnrss.org/frontpage",
        "https://techcrunch.com/feed/",
    ],
    "creative": [
        "https://www.designboom.com/feed/",
        "https://www.creativebloq.com/feeds/rss",
    ],
}

def _fetch_rss(url: str, domain: str, limit: int = 3) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            summary = summary[:600]
            if title and summary:
                results.append({
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "domain": domain,
                })
        return results
    except Exception as e:
        print(f"[collector] Failed {url}: {e}")
        return []


def _fetch_self_determined(keywords: list[str]) -> list[dict]:
    if not keywords:
        return []
    keyword = keywords[0].replace(" ", "+")
    url = f"http://export.arxiv.org/api/query?search_query=ti:{keyword}&max_results=2"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()[:600]
            if title and summary:
                results.append({
                    "title": title,
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "domain": "self_determined",
                })
        return results
    except Exception as e:
        print(f"[collector] Self-determined fetch failed: {e}")
        return []


def collect_all(self_log: dict) -> list[dict]:
    articles = []

    for domain, urls in RSS_SOURCES.items():
        for url in urls:
            articles.extend(_fetch_rss(url, domain))

    self_keywords = self_log.get("keywords", {}).get("self_determined", [])
    articles.extend(_fetch_self_determined(self_keywords))

    seen = set()
    unique = []
    for a in articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)

    return unique[:10]
