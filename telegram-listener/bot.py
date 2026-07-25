import asyncio
import json
import os
import re
from datetime import datetime, time

import requests
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

from config import (
    API_ID,
    API_HASH,
    AIRFLOW_API_BASE,
    AIRFLOW_USERNAME,
    AIRFLOW_PASSWORD,
)

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "airflow", "shared", "downloads")


def get_airflow_variable(key):
    try:
        response = requests.get(
            f"{AIRFLOW_API_BASE}/{key}",
            auth=(AIRFLOW_USERNAME, AIRFLOW_PASSWORD),
        )
        response.raise_for_status()
        return response.json()["value"]
    except Exception as e:
        print(f"❌ Failed to fetch variable \"{key}\": {e}")
        return None


def sanitize_filename(text):
    step1 = re.sub(r'[^\u0600-\u06FF\w\s\-_()]', ' ', text)
    step2 = re.sub(r'\s+', ' ', step1)
    return step2[:50].strip()


async def main():
    group_name = get_airflow_variable("group_name")
    author_names_raw = get_airflow_variable("author_names")

    author_names = {}
    try:
        author_names = json.loads(author_names_raw or "{}")
    except Exception as e:
        print(f"❌ Failed to parse author_names: {e}")

    if not group_name:
        print("❌ group_name variable not set!")
        return

    now = datetime.now()
    today_date = now.strftime("%d %B")
    print(f"📥 Fetching {today_date} images")

    session_path = os.path.join(os.path.dirname(__file__), "session", "bot")
    client = TelegramClient(session_path, API_ID, API_HASH)

    await client.start()
    print("✅ Telegram is ready!")

    target_group = None
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.name == group_name:
            target_group = dialog.entity
            break

    if not target_group:
        print("❌ Group not found!")
        await client.disconnect()
        return

    start_of_today = datetime.combine(now.date(), time.min)

    async for message in client.iter_messages(target_group, limit=500):
        if not isinstance(message.media, MessageMediaPhoto):
            continue

        msg_date = message.date.replace(tzinfo=None)
        if msg_date < start_of_today or msg_date > now:
            continue

        try:
            sender_id = message.sender_id
            if not sender_id:
                continue

            author_name = author_names.get(str(sender_id), str(sender_id))

            folder_path = os.path.join(DOWNLOADS_DIR, author_name)
            os.makedirs(folder_path, exist_ok=True)

            caption_part = ""
            if message.text:
                clean = sanitize_filename(message.text)
                if clean:
                    caption_part = f"({clean})"

            filename = (
                f"photo_{message.id}_{int(message.date.timestamp())}"
                f"{caption_part}.jpg"
            )

            filepath = os.path.join(folder_path, filename)

            await client.download_media(
                message,
                file=filepath
            )

            print(f"✅ Saved: {filename} from {author_name}")
        except Exception as e:
            print(f"❌ Error saving media: {e}")

    print("✅ Done. Exiting...")
    print("***********************************")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
