import sys
from pathlib import Path

import toml
from loguru import logger
from pydantic import BaseModel


class Mastodon(BaseModel):
    client_id: str
    client_secret: str
    access_token: str
    api_base_url: str


class Telegram(BaseModel):
    bot_token: str
    channel_name: str


class ConfigModel(BaseModel):
    mastodon: Mastodon
    telegram: Telegram


class Config:
    config: ConfigModel

    def __init__(self):
        if not Path("config.toml").exists():
            logger.error("The config file does not exist!")
            sys.exit()

        with open("config.toml") as f:
            self.config = ConfigModel.parse_obj(toml.load(f))
