import asyncio
from io import BytesIO
from typing import List

from loguru import logger
from mastodon import Mastodon

from .config import Config
from .message import MastodonMessage, Media


class MastodonImpl:
    def __init__(self):
        config = Config()
        self.mastodon = Mastodon(client_id=config.config.mastodon.client_id,
                                 access_token=config.config.mastodon.access_token,
                                 client_secret=config.config.mastodon.client_secret,
                                 api_base_url=config.config.mastodon.api_base_url)

    async def send_toot(self, message: MastodonMessage):
        media_ids = await self.upload_media(message.medias)
        self.mastodon.status_post(message.text, media_ids=media_ids)
        logger.info(f"Toot '{message.text}' Has been sent")

    async def upload_media(self, media: List[Media]):
        media_ids = []
        for i in media:
            preview_media_id = self.mastodon.media_post(BytesIO(i.content), mime_type=i.mimetype)
            await self.wait_media_upload(preview_media_id)
            media_id = self.mastodon.media(preview_media_id)
            media_ids.append(media_id)
        return media_ids

    async def wait_media_upload(self, preview_media_id):
        while True:
            photo_url = self.mastodon.media(preview_media_id).get("url")
            if not bool(photo_url):
                await asyncio.sleep(3)
            else:
                break
