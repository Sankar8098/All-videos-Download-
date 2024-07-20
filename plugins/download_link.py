import asyncio
import os
import sys
import time
import math
import youtube_dl
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Config
from helper.utils import (
    download_progress_hook,
    get_thumbnail_url,
    ytdl_downloads,
    get_porn_thumbnail_url,
    progress_for_pyrogram,
    download_thumbnail,
)

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

        thumbnail_filename = await download_thumbnail(thumbnail)
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
                        progress_args=(msg, time.time())
                    )
                    os.remove(file)
                    if thumbnail_filename:
                        os.remove(thumbnail_filename)
                    break
                except Exception as e:
                    print("⚠️  ERROR:- ", e)
                    break

downloader = Downloader()

def progress_for_pyrogram(current, total, msg, start_time):
    elapsed_time = time.time() - start_time
    if elapsed_time < 1:
        elapsed_time = 1
    speed = current / elapsed_time
    time_to_completion = (total - current) / speed
    percentage = current * 100 / total

    progress_str = "[{0}{1}] {2}%\n".format(
        ''.join(["▰" for i in range(math.floor(percentage / 5))]),
        ''.join(["▱" for i in range(20 - math.floor(percentage / 5))]),
        round(percentage, 2)
    )

    time_text = "• Elapsed: {}s\n• ETA: {}s".format(
        round(elapsed_time, 2),
        round(time_to_completion, 2)
    )

    try:
        msg.edit(f"⚠️ Please Wait...\n\n**Uploading Started...**\n\n{progress_str}\n{time_text}")
    except Exception as e:
        print(e)

def download_progress_hook(d, msg, link):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        current = d.get('downloaded_bytes')
        start_time = d.get('start_time')
        progress_for_pyrogram(current, total, msg, start_time)

async def ytdl_downloads(bot, update, link):
    msg = await update.message.reply_text("Downloading... Please have patience", disable_web_page_preview=True)

    ytdl_opts = {
        'format': 'best',
        'progress_hooks': [lambda d: download_progress_hook(d, msg, link)]
    }

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        try:
            ydl.download([link])
        except youtube_dl.utils.DownloadError as e:
            await msg.edit(f"Sorry, there was a problem with that particular video: {e}")
            return

    await msg.edit("⚠️ Please Wait...\n\n**Trying to Upload....**")
    await downloader._upload_video(bot, update, msg, None)

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
