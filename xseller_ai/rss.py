from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass
from typing import Iterable, List

import feedparser
import requests
import certifi


logger = logging.getLogger(__name__)


@dataclass
class Article:
    uid: str
    title: str
    link: str
    summary: str
    published_at: dt.datetime
    source: str


def parse_entry(entry, default_source: str) -> Article | None:
    if not entry.get("title") or not entry.get("link"):
        return None

    published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if published_parsed:
        published_at = dt.datetime(*published_parsed[:6], tzinfo=dt.timezone.utc)
    else:
        published_at = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)

    summary = (
        entry.get("summary")
        or entry.get("description")
        or entry.get("content", [{}])[0].get("value", "")
    )

    uid = entry.get("id") or entry.get("guid") or entry.get("link")

    return Article(
        uid=uid,
        title=entry.get("title", "").strip(),
        link=entry.get("link", "").strip(),
        summary=(summary or "").strip(),
        published_at=published_at,
        source=entry.get("source", {}).get("title", default_source) or default_source,
    )


def fetch_feeds(feeds: Iterable[str], since_hours: int = 24) -> List[Article]:
    cutoff = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) - dt.timedelta(
        hours=since_hours
    )
    collected: list[Article] = []
    for feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=15, verify=certifi.where(), headers={"User-Agent": "xseller-ai-bot/1.0"})
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch feed %s: %s", feed_url, exc)
            continue
        if parsed.bozo:
            logger.warning("Failed to parse feed %s: %s", feed_url, parsed.bozo_exception)
            continue
        source_title = parsed.feed.get("title", feed_url)
        for entry in parsed.entries:
            article = parse_entry(entry, default_source=source_title)
            if not article:
                continue
            if article.published_at < cutoff:
                continue
            collected.append(article)
    # Deduplicate by link
    unique: dict[str, Article] = {}
    for art in sorted(collected, key=lambda a: a.published_at, reverse=True):
        unique.setdefault(art.link, art)
    return list(unique.values())
