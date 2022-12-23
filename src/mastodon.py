import asyncio
from io import BytesIO
from typing import List

from loguru import logger
from mastodon import Mastodon

from .config import Config
from .message import MastodonMessage, Media
from .utils import split_string, split_list

MAX_TEXT_LENGTH = 500


def split_message(message: MastodonMessage):
    split_messages = []
    if len(message.text) > MAX_TEXT_LENGTH:
        texts = split_string(message.text, MAX_TEXT_LENGTH)
    else:
        texts = [message.text]
    for text in texts:
        split_messages.append(MastodonMessage(text=text, medias=[]))
    split_medias = split_list(message.medias, 4)
    for medias in split_medias:
        try:
            match_message = split_messages[split_medias.index(medias)]
            match_message.medias = medias
        except IndexError:
            split_messages.append(MastodonMessage(text=None, medias=medias))
    return split_messages


class MastodonImpl:
    def __init__(self):
        config = Config()
        self.mastodon = Mastodon(client_id=config.config.mastodon.client_id,
                                 access_token=config.config.mastodon.access_token,
                                 client_secret=config.config.mastodon.client_secret,
                                 api_base_url=config.config.mastodon.api_base_url)

    async def send_toot(self, message: MastodonMessage):
        if len(message.text) > MAX_TEXT_LENGTH or len(message.medias) > 4:
            messages = split_message(message)
            toots = []
            last_toot_id = None
            for msg in messages:
                media_ids = await self.upload_media(msg.medias)
                toot = self.mastodon.status_post(msg.text, media_ids=media_ids, in_reply_to_id=last_toot_id)
                logger.info(f"Toot '{msg.text}' Has been sent")
                toots.append(toot)
                last_toot_id = toot["id"]
            return toots
        else:
            media_ids = await self.upload_media(message.medias)
            toot = self.mastodon.status_post(message.text, media_ids=media_ids)
            logger.info(f"Toot '{message.text}' Has been sent")
            return [toot]

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
