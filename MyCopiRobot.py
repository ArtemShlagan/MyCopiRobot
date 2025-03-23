import os
import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import SessionPasswordNeededError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MyCopiRobot')

api_id = '23415626'
api_hash = '84407a767ffbbd9ce175bb9dba5948f2'

channel_pairs = [
    ('@cpa_lenta', -1002615921992),
    ('@photoshopforyou', -1002510401792),
    ('@smmplanner', -1002572828500),
    ('@markin_seo', -1002611064574),
    ('@abbsol', -1002505822535),
    ('@codecamp', -1002619401042),
    ('@photoshop_hack', -1002541197657),
    ('@floor_99', -1002611064574),
    ('@WBtimn', -1002500048265),
    ('@heymoneymaker', -1002611064574),
]

session_path = os.getenv('SESSION_PATH', 'session_name')  # Файл сессии
phone_number = os.getenv('PHONE_NUMBER')  # Номер из переменной окружения

client = TelegramClient(session_path, api_id, api_hash)

sent_messages = {}

async def process_message(message, source_channel, target_channel):
    if message.id in sent_messages.get(target_channel, []):
        return

    text = message.text.strip() if message.text else ""

    media_files = []
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            media_files.append(message.photo)
        elif isinstance(message.media, MessageMediaDocument):
            media_files.append(message.document)

    try:
        if media_files:
            await client.send_file(target_channel, media_files[0], caption=text)
        else:
            await client.send_message(target_channel, text)
        logger.info(f"Сообщение {message.id} отправлено в {target_channel}")
        sent_messages.setdefault(target_channel, []).append(message.id)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в {target_channel}: {e}")

async def main():
    try:
        if phone_number:
            await client.start(phone_number)
        else:
            await client.start()
    except SessionPasswordNeededError:
        logger.error("Необходим пароль для входа в аккаунт")
        return
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        return

    last_message_ids = {source: None for source, target in channel_pairs}

    while True:
        for source_channel, target_channel in channel_pairs:
            if last_message_ids[source_channel] is None:
                async for message in client.iter_messages(source_channel, limit=1):
                    last_message_ids[source_channel] = message.id

            async for message in client.iter_messages(source_channel, min_id=last_message_ids[source_channel]):
                if message:
                    last_message_ids[source_channel] = message.id
                    await process_message(message, source_channel, target_channel)

        await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())

