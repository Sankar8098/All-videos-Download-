import asyncio
import os
import time
import uuid
import requests
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
import youtube_dl
from moviepy.editor import VideoFileClip
from config import Config
from helper.utils import (
    download_progress_hook,
    get_thumbnail_url,
    get_porn_thumbnail_url,
    progress_for_pyrogram,
)
import nest_asyncio

nest_asyncio.apply()

class Downloader:
    def __init__(self):
        self.queue_links = {}

    async def download_multiple(self, bot, update, link_msg, index=0):
        user_id = update.from_user.id
        if user_id not in self.queue_links:
            self.queue_links[user_id] = [link_msg.text.strip()]

        current_link = self.queue_links[user_id][index]
        msg = await update.reply_text(
            f"**{index + 1}. Link:-** {current_link}\n\nDownloading... Please Have Patience\n 𝙇𝙤𝙖𝙙𝙞𝙣𝙜...\n\n⚠️ **Please note that for multiple downloads, the progress may not be immediately apparent. Therefore, if it appears that nothing is downloading, please wait a few minutes as the downloads may be processing in the background. The duration of the download process can also vary depending on the content being downloaded, so we kindly ask for your patience.**",
            disable_web_page_preview=True
        )

        # Set options for youtube-dl
        if current_link.startswith("https://www.pornhub"):
            thumbnail = get_porn_thumbnail_url(current_link)
        else:
            thumbnail = get_thumbnail_url(current_link)

        ytdl_opts = {
            'format': 'best',
            'progress_hooks': [lambda d: download_progress_hook(d, msg, current_link)]
        }

        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            try:
                await asyncio.get_event_loop().run_in_executor(None, ydl.download, [current_link])
            except youtube_dl.utils.DownloadError as e:
                await msg.edit(f"Sorry, There was a problem with that particular video: {e}")
                await self._proceed_to_next(bot, update, link_msg, index + 1)
                return

        thumbnail_filename = await self._download_thumbnail(thumbnail)
        await msg.edit("⚠️ Please Wait...\n\n**Trying to Upload....**")
        await self._upload_video(bot, update, msg, thumbnail_filename)

        await msg.delete()
        await self._proceed_to_next(bot, update, link_msg, index + 1)

    async def _proceed_to_next(self, bot, update, link_msg, next_index):
        user_id = update.from_user.id
        if next_index < len(self.queue_links[user_id]):
            await self.download_multiple(bot, update, link_msg, next_index)
        else:
            await update.reply_text(f"𝒜𝐿𝐿 𝐿𝐼𝒩𝒦𝒮 𝒟𝒪𝒲𝒩𝐿𝒪𝒜𝒟𝐸𝒟 𝒮𝒰𝒞𝒞𝐸𝒮𝒮𝐹𝒰𝐿𝐿𝒴 ✅", reply_to_message_id=link_msg.id)

    async def _download_thumbnail(self, thumbnail_url):
        if not thumbnail_url:
            return None

        unique_id = uuid.uuid4().hex
        thumbnail_filename = f"thumbnail_{unique_id}.jpg"
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            with open(thumbnail_filename, 'wb') as f:
                f.write(response.content)
            return thumbnail_filename
        return None

    async def _upload_video(self, bot, update, msg, thumbnail_filename):
        user_id = update.from_user.id
        for file in os.listdir('.'):
            if file.endswith(".mp4") or file.endswith('.mkv'):
                try:
                    # Extract duration using moviepy
                    clip = VideoFileClip(file)
                    duration = int(clip.duration)
                    clip.close()

                    # Format duration to HH:MM:SS
                    hours, remainder = divmod(duration, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

                    await bot.send_video(
                        chat_id=user_id,
                        video=file,
                        thumb=thumbnail_filename if thumbnail_filename else None,
                        caption=f"**📁 File Name:- `{file}`\n\nDuration: {formatted_duration}\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}",
                        progress=progress_for_pyrogram,
                        progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time())
                    )
                    os.remove(file)
                    if thumbnail_filename:
                        os.remove(thumbnail_filename)
                    break
                except Exception as e:
                    await msg.edit(str(e))
                    break
            else:
                continue

async def start_bot():
    bot = Client(
        "my_account",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins")
    )

    try:
        await bot.start()
    except FloodWait as e:
        print(f"Flood wait error: waiting for {e.x} seconds.")
        await asyncio.sleep(e.x)
        await bot.start()

    @bot.on_message(filters.command(["start"]))
    async def start(_, message: Message):
        await message.reply_text("Hello! Send me a link to download.")

    @bot.on_message(filters.text & filters.private)
    async def download_video(_, message: Message):
        link = message.text.strip()
        if "http" in link:
            downloader = Downloader()
            await downloader.download_multiple(bot, message, message)
        else:
            await message.reply_text("Please send a valid link.")

    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(start_bot())
