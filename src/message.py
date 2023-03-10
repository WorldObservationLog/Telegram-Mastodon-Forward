from io import BytesIO
from typing import List, Optional

from PIL import Image
from telegram import Message
from telegram.helpers import effective_message_type


class Media:
    content: bytearray
    mimetype: str

    def __init__(self, content: bytearray, mimetype: str):
        self.content = content
        self.mimetype = mimetype


class Photo(Media):
    def __init__(self, content: bytearray):
        super().__init__(content, "")
        self.mimetype = Image.MIME[Image.open(BytesIO(content)).format]


class Audio(Media):
    pass


class Video(Media):
    pass


MESSAGE_TYPE = {"photo": Photo, "audio": Audio, "video": Video}


class MastodonMessage:
    text: Optional[str]
    medias: List[Optional[Media]]

    def __init__(self, text, medias):
        self.text = ""
        if bool(text):
            self.text = text
        self.medias = medias

    @classmethod
    async def from_telegram_message(cls, message: Message):
        text = message.text if message.text else message.caption
        medias = await cls.handle_different_media(message)
        return cls(text=text, medias=medias)

    @classmethod
    async def from_multi_telegram_messages(cls, messages: List[Message]):
        text = ""
        medias = []
        for i in messages:
            if i.text:
                text = i.text
            elif i.caption:
                text = i.caption
            medias.extend(await cls.handle_different_media(i))
        return cls(text=text, medias=medias)

    @classmethod
    async def handle_different_media(cls, message):
        medias = []
        message_type = MESSAGE_TYPE.get(effective_message_type(message))
        if message_type is Photo:
            content = await (await message.photo[-1].get_file()).download_as_bytearray(bytearray())
            medias.append(message_type(content=content))
        elif message_type:
            file = message.effective_attachment
            content = await (await file.get_file()).download_as_bytearray(bytearray())
            medias.append(message_type(content=content, mimetype=file.mime_type))
        return medias
