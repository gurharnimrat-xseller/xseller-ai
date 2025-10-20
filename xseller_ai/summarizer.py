from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List

from .rss import Article
from . import settings as settings_module

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI  # type: ignore
except ImportError:
    OpenAI = None  # type: ignore


@dataclass
class Script:
    id: str
    title: str
    link: str
    summary: str
    why_it_matters: str
    what_happened: str
    whats_next: str


def fallback_summary(article: Article) -> Script:
    summary = article.summary or "Summary not available."
    sentences = summary.split(". ")
    why = sentences[0] if sentences else summary
    what = sentences[1] if len(sentences) > 1 else article.title
    nxt = sentences[2] if len(sentences) > 2 else "Watch this space for further developments."
    return Script(
        id=article.uid,
        title=article.title,
        link=article.link,
        summary=summary.strip(),
        why_it_matters=why.strip(),
        what_happened=what.strip(),
        whats_next=nxt.strip(),
    )


def get_openai_client():
    global OpenAI  # type: ignore
    if OpenAI is None:
        try:
            from openai import OpenAI as OpenAIClass  # type: ignore
        except ImportError:
            logger.warning("openai package not available; install `openai` to enable summaries.")
            return None
        OpenAI = OpenAIClass
    if not settings_module.settings.openai_api_key:
        return None
    try:
        return OpenAI(api_key=settings_module.settings.openai_api_key)  # type: ignore
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to initialise OpenAI client: %s", exc)
        return None


def llm_summary(article: Article) -> Script:
    client = get_openai_client()
    if client is None:
        logger.warning("OpenAI client not available; using fallback summary.")
        return fallback_summary(article)

    prompt = (
        "Summarize the article using the framework:\n"
        "Why it matters → What happened → What's next.\n"
        "Return output as JSON with keys: why_it_matters, what_happened, whats_next, summary.\n"
        f"Title: {article.title}\n"
        f"Link: {article.link}\n"
        f"Body:\n{article.summary}\n"
    )
    try:
        completion = client.responses.create(
            model=settings_module.settings.openai_model,
            input=prompt,
            max_output_tokens=400,
            temperature=0.3,
        )
        content = completion.output[0].content[0].text  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001
        logger.error("OpenAI summary failed: %s", exc)
        return fallback_summary(article)

    import json

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        logger.warning("Unexpected LLM response; falling back.")
        return fallback_summary(article)

    return Script(
        id=article.uid,
        title=article.title,
        link=article.link,
        summary=payload.get("summary", article.summary),
        why_it_matters=payload.get("why_it_matters", ""),
        what_happened=payload.get("what_happened", ""),
        whats_next=payload.get("whats_next", ""),
    )


def summarize_articles(articles: Iterable[Article]) -> List[Script]:
    scripts: list[Script] = []
    for article in articles:
        scripts.append(llm_summary(article))
    return scripts
