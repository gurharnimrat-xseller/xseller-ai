from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .summarizer import Script

DEFAULT_HASHTAGS = [
    "#AI",
    "#TechNews",
    "#ArtificialIntelligence",
    "#Automation",
]


@dataclass
class PlatformPost:
    caption: str
    image_prompt: str | None = None
    image_path: str | None = None


@dataclass
class SocialPost:
    id: str
    story_title: str
    platforms: Dict[str, PlatformPost] = field(default_factory=dict)


def build_hashtags(limit: int = 3) -> str:
    return " ".join(DEFAULT_HASHTAGS[:limit])


def twitter_caption(script: Script) -> str:
    hashtags = build_hashtags(2)
    return f"{script.why_it_matters} {hashtags}"


def linkedin_caption(script: Script) -> str:
    hashtags = build_hashtags(3)
    return (
        f"{script.title}\n\n"
        f"{script.what_happened}\n\n"
        f"Why it matters: {script.why_it_matters}\n"
        f"What's next: {script.whats_next}\n\n"
        f"{hashtags}"
    )


def instagram_caption(script: Script) -> str:
    hashtags = build_hashtags(3)
    return (
        f"🚀 {script.title}\n\n"
        f"{script.why_it_matters}\n"
        f"{script.what_happened}\n"
        f"Next: {script.whats_next}\n\n"
        f"👇 Follow @xseller.ai for daily AI drops\n"
        f"{hashtags}"
    )


def facebook_caption(script: Script) -> str:
    hashtags = build_hashtags(2)
    return (
        f"{script.title}\n\n"
        f"{script.why_it_matters}\n"
        f"{script.what_happened}\n"
        f"What's next: {script.whats_next}\n\n"
        f"{hashtags}"
    )


def build_social_posts(scripts: Iterable[Script]) -> List[SocialPost]:
    posts: list[SocialPost] = []
    for script in scripts:
        social = SocialPost(
            id=script.id,
            story_title=script.title,
            platforms={
                "X": PlatformPost(
                    caption=twitter_caption(script),
                    image_prompt=f"Minimal AI news card featuring '{script.title}' headline with neon accents.",
                ),
                "LinkedIn": PlatformPost(
                    caption=linkedin_caption(script),
                    image_prompt=f"Professional gradient header summarizing '{script.title}' with AI iconography.",
                ),
                "Instagram": PlatformPost(
                    caption=instagram_caption(script),
                    image_prompt=f"Bold square poster with '{script.title}' and futuristic typography.",
                ),
                "Facebook": PlatformPost(
                    caption=facebook_caption(script),
                    image_prompt=f"Friendly AI themed news card highlighting '{script.title}'.",
                ),
            },
        )
        posts.append(social)
    return posts
