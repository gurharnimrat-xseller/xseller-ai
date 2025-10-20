from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    elevenlabs_api_key: str | None = None
    repurpose_api_key: str | None = None
    notion_token: str | None = None
    notion_db_id: str | None = None
    posting_mode: str = "manual"
    outputs_dir: str = "outputs"
    data_dir: str = "data"

    def __post_init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.repurpose_api_key = os.getenv("REPURPOSE_API_KEY")
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_db_id = os.getenv("NOTION_DB_ID")
        self.posting_mode = os.getenv("POSTING_MODE", self.posting_mode)
        self.outputs_dir = os.getenv("OUTPUTS_DIR", self.outputs_dir)
        self.data_dir = os.getenv("DATA_DIR", self.data_dir)


settings = Settings()


def reload() -> Settings:
    global settings
    settings = Settings()
    return settings
