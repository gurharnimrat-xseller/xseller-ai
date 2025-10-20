from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
import sys
import re

from dotenv import load_dotenv
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from xseller_ai import hooks, queue, ranking, rss, settings, social, summarizer, tts


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ai-news-runner")

FEEDS = [
    "https://techcrunch.com/tag/ai/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/tag/artificial-intelligence/feed/",
    "https://openai.com/blog/rss.xml",
    "https://arxiv.org/rss/cs.AI",
]


def create_image(path: Path, headline: str, prompt: str, size=(1080, 1080)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=(10, 14, 24))
    draw = ImageDraw.Draw(img)
    text = headline[:120]
    draw.multiline_text((40, 40), text, fill=(0, 245, 160), spacing=10)
    footer = prompt[:200]
    draw.multiline_text((40, size[1] - 160), footer, fill=(200, 200, 200), spacing=8)
    img.save(path)


def write_social_text(path: Path, posts: list[social.SocialPost]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for post in posts:
        for platform, platform_post in post.platforms.items():
            file = path / f"{post.id}_{platform.lower()}.txt"
            file.write_text(platform_post.caption, encoding="utf-8")


def write_video_manifest(path: Path, scripts: list[summarizer.Script]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    manifest = [
        {
            "id": script.id,
            "title": script.title,
            "summary": script.summary,
            "why_it_matters": script.why_it_matters,
            "what_happened": script.what_happened,
            "whats_next": script.whats_next,
        }
        for script in scripts
    ]
    (path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def sanitize_filename(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return slug.strip("_") or "audio"


def main() -> None:
    load_dotenv(dotenv_path=ROOT / ".env", override=True)
    settings.reload()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    outputs_root = Path(settings.settings.outputs_dir) / today
    video_dir = outputs_root / "video"
    social_dir = outputs_root / "social"
    audio_dir = outputs_root / "audio"

    logger.info("Fetching AI news feeds...")
    articles = rss.fetch_feeds(FEEDS, since_hours=24)
    if not articles:
        logger.warning("No articles found in the last 24 hours.")
        return

    ranked = ranking.rank_articles(articles, top_n=5)
    top_articles = [item.article for item in ranked]

    logger.info("Summarising top articles... (OpenAI key detected=%s)", bool(settings.settings.openai_api_key))
    scripts = summarizer.summarize_articles(top_articles)

    logger.info("Generating hook variants...")
    hook_sets = hooks.generate_hooks(scripts)

    logger.info("Preparing social posts...")
    social_posts = social.build_social_posts(scripts)

    logger.info("Rendering placeholder social images...")
    for social_post in social_posts:
        for platform, platform_post in social_post.platforms.items():
            image_path = social_dir / f"{social_post.id}_{platform.lower()}.png"
            create_image(image_path, social_post.story_title, platform_post.image_prompt or "")
            platform_post.image_path = str(image_path)

    write_social_text(social_dir, social_posts)
    write_video_manifest(video_dir, scripts)

    audio_paths: dict[str, str] = {}
    logger.info("Generating ElevenLabs voiceovers (if configured)...")
    for script in scripts:
        audio_path = audio_dir / f"{sanitize_filename(script.id)}.mp3"
        generated = tts.synthesize_speech(
            script.summary,
            audio_path,
        )
        if generated:
            audio_paths[script.id] = str(generated)

    logger.info("Updating dashboard queue...")
    data_dir = Path(settings.settings.data_dir)
    queue_path = data_dir / "ai_shorts_queue.json"
    db_path = data_dir / "ai_shorts_db.json"
    queue.merge_into_queue(
        queue_path,
        scripts,
        hook_sets,
        social_posts,
        db_path=db_path,
        audio_paths=audio_paths,
    )

    logger.info("Run completed. Outputs stored in %s", outputs_root)


if __name__ == "__main__":
    main()
