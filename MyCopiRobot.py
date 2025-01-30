import os
import asyncio
import logging
import re
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import SessionPasswordNeededError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TITATOBA')

api_id = '23415626'
api_hash = '84407a767ffbbd9ce175bb9dba5948f2'

channel_pairs = [
    ('@u_now', '@INFOpuls247'),
    ('@smolii_ukraine', '@alarm_ua_24l7'),
    ('@povitryanatrivogaaa', '@AirmapsofUkraine'),
    ('@uniannet', '@UA_Live24I7'),
    ('@kiev_writes', '@Kyivofficial24l7'),
]

# Чтение пути сессионного файла и номера телефона из переменных окружения
session_path = os.getenv('SESSION_PATH', 'session_name')  # по умолчанию 'session_name'
phone_number = os.getenv('PHONE_NUMBER')  # получаем номер из переменной окружения

client = TelegramClient('session_name', api_id, api_hash)

sent_messages = {}

blacklist_phrases = [
    r"⚡️ Підписатися на ONews Україна \| Запропонувати новину",
    r"Підпишися на OKO \| Купимо твої фото та відео",
    r"Київ пише\s*✍️?",
    r"ТРУХА⚡️Україна \| Надіслати новину",
    r"🇺🇦 УС / Підписатися",
    r"ТРУХА",
]

username_pattern = r"@\w+"
tg_link_pattern = r"https://t\.me/\S+"
bracket_pattern = r"\[[^\]]*\]"
emoji_pattern = r"[⚡️✍️]"

def clean_text(text):
    if not text:
        return ""

    for phrase in blacklist_phrases:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    text = re.sub(username_pattern, "", text)
    text = re.sub(tg_link_pattern, "", text)
    text = re.sub(emoji_pattern, "", text)
    text = re.sub(bracket_pattern, "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text

async def process_message(message, target_channel):
    if message.id in sent_messages.get(target_channel, []):
        return

    text = clean_text(message.text if message.text else "")

    if not text:
        return  

    media_files = []
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            media_files.append(message.photo)
        elif isinstance(message.media, MessageMediaDocument):
            media_files.append(message.document)

    if media_files:
        try:
            await client.send_file(target_channel, media_files[0], caption=text)
        except Exception as e:
            logger.error(f"Ошибка отправки в {target_channel}: {e}")
    else:
        try:
            await client.send_message(target_channel, text)
        except Exception as e:
            logger.error(f"Ошибка отправки текста в {target_channel}: {e}")

    sent_messages.setdefault(target_channel, []).append(message.id)

async def main():
    try:
        # Если номер телефона не передан, то попросим ввести
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
                    await process_message(message, target_channel)

        await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())
