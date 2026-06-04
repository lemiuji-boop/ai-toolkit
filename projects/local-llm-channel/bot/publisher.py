# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Publish approved posts to Telegram channel."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.models import Post, PostStatus


async def publish_post(
    session: AsyncSession,
    post: Post,
    *,
    channel_id: str | None = None,
) -> int:
    """Publish post to channel; returns telegram message id."""
    settings = get_settings()
    token = settings.tg_bot_token
    if not token:
        raise RuntimeError("TG_BOT_TOKEN not set")
    ch = channel_id or settings.tg_test_channel_id or settings.tg_channel_id
    if not ch:
        raise RuntimeError("TG_CHANNEL_ID or TG_TEST_CHANNEL_ID not set")

    bot = Bot(token=token)
    try:
        media = [p for p in post.media_paths if Path(p).exists()]
        if media:
            photos = [InputMediaPhoto(media=FSInputFile(p)) for p in media[:10]]
            if len(post.body_md) <= 1024 and photos:
                photos[0].caption = post.body_md
            msgs = await bot.send_media_group(
                chat_id=ch,
                media=photos,  # type: ignore[arg-type]
            )
            msg_id = msgs[0].message_id
            if len(post.body_md) > 1024:
                extra = await bot.send_message(chat_id=ch, text=post.body_md)
                msg_id = extra.message_id
        else:
            sent = await bot.send_message(chat_id=ch, text=post.body_md)
            msg_id = sent.message_id
    finally:
        await bot.session.close()

    post.status = PostStatus.published
    post.published_at = datetime.now(UTC)
    post.tg_message_id = msg_id
    await session.flush()
    return msg_id
