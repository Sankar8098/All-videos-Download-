import asyncio
import os
import sys
import time
import uuid
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import youtube_dl
from config import Config
from helper.utils import (
    get_thumbnail_url,
    get_porn_thumbnail_url,
    ytdl_downloads,
    progress_for_pyrogram,
)

# Define Downloader class and functions
class Downloader:
    def __init__(self):
        self.queue_links = {}

    async def download_multiple(self, bot, update, link_msg, index=0):
        user_id = update.from_user.id
        current_link = self.queue_links[user_id][index]
        msg = await update.message.reply_text(
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
                ydl.download([current_link])
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
            await update.message.reply_text(f"𝒜𝐿𝐿 𝐿𝐼𝒩𝒦𝒮 𝒟𝒪𝒲𝒩𝐿𝒪𝒜𝒟𝐸𝒟 𝒮𝒰𝒞𝒞𝐸𝒮𝒮𝐹𝒰𝐿𝐿𝒴 ✅", reply_to_message_id=link_msg.id)

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
                    await bot.send_video(
                        chat_id=user_id,
                        video=file,
                        thumb=thumbnail_filename if thumbnail_filename else None,
                        caption=f"**📁 File Name:- `{file}`\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}",
                        progress=progress_for_pyrogram,
                        progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time())
                    )
                    os.remove(file)
                    if thumbnail_filename:
                        os.remove(thumbnail_filename)
                    break
                except Exception as e:
                    print("⚠️  ERROR:- ", e)
                    break

downloader = Downloader()

@Client.on_message(filters.regex(pattern=r"(?=.*https://)(?!.*\bmega\b).*") & filters.user(Config.ADMIN))
async def handle_yt_dl(bot: Client, cmd: Message):
    await cmd.reply_text(
        "**Do you want to download this file ?**", 
        reply_to_message_id=cmd.id, 
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('🔻 Download 🔻', callback_data='http_link')],
            [InlineKeyboardButton('🖇️ Add Multiple Links 🖇️', callback_data='multiple_http_link')]
        ])
    )

@Client.on_callback_query(filters.regex('^http_link'))
async def handle_single_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text
    await ytdl_downloads(bot, update, http_link)

@Client.on_callback_query(filters.regex('^multiple_http_link'))
async def handle_multiple_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text
    user_id = update.from_user.id

    if user_id not in downloader.queue_links:
        downloader.queue_links[user_id] = [http_link]
        await update.message.delete()
        links_msg = None
        while True:
            link = await bot.ask(chat_id=user_id, text="🔗Send Link to add it to queue 🔗\n\nUse /done when you're done adding links to queue.", filters=filters.text, reply_to_message_id=update.message.id)
            if str(link.text).startswith("https"):
                downloader.queue_links[user_id].append(link.text)
                await update.message.reply_text("Successfully Added To Queue ✅", reply_to_message_id=link.id)
            elif link.text == "/done":
                user_links = downloader.queue_links[user_id]
                links_text = "\n".join([f"{idx+1}. `{link}`" for idx, link in enumerate(user_links)])
                links_msg = await update.message.reply_text(f"👤 <code>{update.from_user.first_name}</code> 🍁\n\n {links_text}")
                break
            else:
                await update.message.reply_text("⚠️ Please Send Valid Link !")
                continue

        await update.message.reply_text("Downloading Started ✅\n\nPlease have patience while it's downloading it may take sometimes...")
        try:
            await downloader.download_multiple(bot, update, links_msg)
        except Exception as e:
            print(f'Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__} - {e}')
