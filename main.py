from typing import cast, List

from loguru import logger
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackContext

from src.config import Config
from src.mastodon import MastodonImpl
from src.message import MastodonMessage

mastodon = MastodonImpl()
config = Config()


async def media_group_handler(context: CallbackContext):
    context.job.data = cast(List[Message], context.job.data)
    medias = []
    for message in context.job.data:
        medias.append(message)
    if not medias:
        return
    message = await MastodonMessage.from_multi_telegram_messages(medias)
    await mastodon.send_toot(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_message.chat.title}: {update.effective_message.text}")
    if update.effective_message.media_group_id:
        telegram_message = update.effective_message
        jobs = context.job_queue.get_jobs_by_name(str(telegram_message.media_group_id))
        if jobs:
            jobs[0].data.append(telegram_message)
        else:
            context.job_queue.run_once(callback=media_group_handler, when=2, data=[telegram_message],
                                       name=str(telegram_message.media_group_id))
        return
    message = await MastodonMessage.from_telegram_message(update.effective_message)
    await mastodon.send_toot(message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.config.telegram.bot_token).build()

    message_handler = MessageHandler(filters.Chat(username=config.config.telegram.channel_name), handle_message)
    application.add_handler(message_handler)

    application.run_polling()
