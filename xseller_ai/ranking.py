from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List

from .rss import Article

VIRAL_KEYWORDS = {
    "funding": 2.0,
    "raises": 2.0,
    "launch": 1.5,
    "google": 1.4,
    "openai": 1.6,
    "microsoft": 1.3,
    "nvidia": 1.6,
    "elon": 1.5,
    "partnership": 1.2,
    "billion": 1.3,
    "trillion": 1.4,
    "breakthrough": 1.8,
}


@dataclass
class RankedArticle:
    article: Article
    score: float


def keyword_score(text: str) -> float:
    text_lower = text.lower()
    score = 0.0
    for keyword, weight in VIRAL_KEYWORDS.items():
        if keyword in text_lower:
            score += weight
    return score


def rank_articles(articles: Iterable[Article], top_n: int = 5) -> List[RankedArticle]:
    ranked: list[RankedArticle] = []
    for art in articles:
        base_score = 1.0
        time_bonus = 1.0 / (1.0 + math.exp((art.published_at.hour - 12) / 3))
        title_score = keyword_score(art.title)
        summary_score = keyword_score(art.summary)
        total = base_score + time_bonus + title_score + 0.5 * summary_score
        ranked.append(RankedArticle(article=art, score=total))
    ranked.sort(key=lambda r: r.score, reverse=True)
    return ranked[:top_n]
