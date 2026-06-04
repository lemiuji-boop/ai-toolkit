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

"""Draft review flow — send to admin with approve/reject."""
from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.models import Post, PostStatus


def review_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Approve", callback_data=f"approve:{post_id}"),
                InlineKeyboardButton(text="Reject", callback_data=f"reject:{post_id}"),
            ],
        ]
    )


async def send_for_review(session: AsyncSession, post: Post) -> None:
    settings = get_settings()
    if not settings.tg_bot_token or not settings.tg_admin_id:
        raise RuntimeError("TG_BOT_TOKEN and TG_ADMIN_ID required for review")
    bot = Bot(token=settings.tg_bot_token)
    try:
        preview = post.body_md[:3500]
        await bot.send_message(
            chat_id=settings.tg_admin_id,
            text=f"Review post #{post.id}\n\n{preview}",
            reply_markup=review_keyboard(post.id),
        )
        post.status = PostStatus.review
        await session.flush()
    finally:
        await bot.session.close()


async def set_post_status(session: AsyncSession, post_id: int, status: PostStatus) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise ValueError(f"Post {post_id} not found")
    post.status = status
    await session.flush()
    return post
