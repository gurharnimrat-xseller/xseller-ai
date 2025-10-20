from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List

from .summarizer import Script


@dataclass
class HookSet:
    script_id: str
    hooks: List[str]


SHOCK_PREFIXES = [
    "⚡️ Shocker:",
    "Breaking:",
    "Heads up:",
    "Just in:",
]

IMPACT_PREFIXES = [
    "Why it matters:",
    "Your takeaway:",
    "What it means for you:",
]


def build_hooks(script: Script) -> HookSet:
    shock = f"{random.choice(SHOCK_PREFIXES)} {script.why_it_matters[:150]}".strip()
    celeb = f"{script.title.split(':')[0]} just made an AI move you can’t ignore."
    impact = f"{random.choice(IMPACT_PREFIXES)} {script.whats_next[:160]}".strip()
    hooks = [shock, celeb, impact]
    return HookSet(script_id=script.id, hooks=hooks)


def generate_hooks(scripts: Iterable[Script]) -> List[HookSet]:
    return [build_hooks(script) for script in scripts]
