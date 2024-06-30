import asyncio
import os
import sys
import time
import uuid
import math
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import youtube_dl
from config import Config
from helper.utils import (
    get_thumbnail_url,
    ytdl_downloads,
    get_porn_thumbnail_url
)

class Downloader:
    def __init__(self):
        self.queue_links = {}

    async def download_multiple(self, bot, update, link_msg, index=0):
        user_id = update.from_user.id
        msg = await update.message.reply_text(
            f"**{index+1}. Link:-** {self.queue_links[user_id][index]}\n\nDownloading... Please Have Patience\n 𝙇𝙤𝙖𝙙𝙞𝙣𝙜...\n\n⚠️ **Please note that for multiple downloads, the progress may not be immediately apparent. Therefore, if it appears that nothing is downloading, please wait a few minutes as the downloads may be processing in the background. The duration of the download process can also vary depending on the content being downloaded, so we kindly ask for your patience.**",
            disable_web_page_preview=True
        )

        if self.queue_links[user_id][index].startswith("https://www.pornhub"):
            thumbnail = get_porn_thumbnail_url(self.queue_links[user_id][index])
        else:
            thumbnail = get_thumbnail_url(self.queue_links[user_id][index])

        ytdl_opts = {
            'format': 'best',
            'progress_hooks': [lambda d: download_progress_hook(d, msg, self.queue_links[user_id][index])]
        }

        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            try:
                ydl.download([self.queue_links[user_id][index]])
            except youtube_dl.utils.DownloadError as e:
                await msg.edit(f"Sorry, There was a problem with that particular video: {e}")
                index += 1
                if index < len(self.queue_links[user_id]):
                    await self.download_multiple(bot, update, link_msg, index)
                else:
                    await update.message.reply_text(f"𝒜𝐿𝐿 𝐿𝐼𝒩𝒦𝒮 𝒟𝒪𝒲𝒩𝐿𝒪𝒜𝒟𝐸𝒟 𝒮𝒰𝒞𝒞𝐸𝒮𝒮𝐹𝒰𝐿𝐿𝒴 ✅", reply_to_message_id=link_msg.id)
                return

        unique_id = uuid.uuid4().hex
        thumbnail_filename = None
        if thumbnail:
            thumbnail_filename = f"p_hub_thumbnail_{unique_id}.jpg"
            response = requests.get(thumbnail)
            if response.status_code == 200:
                with open(thumbnail_filename, 'wb') as f:
                    f.write(response.content)

        await msg.edit("⚠️ Please Wait...\n\n**Trying to Upload....**")

        for file in os.listdir('.'):
            if file.endswith(".mp4") or file.endswith('.mkv'):
                try:
                    await self.send_video(bot, update, file, thumbnail_filename, msg)
                    break
                except Exception as e:
                    print("⚠️  ERROR:- ", e)
                    break

        await msg.delete()

        index += 1
        if index < len(self.queue_links[user_id]):
            await self.download_multiple(bot, update, link_msg, index)
        else:
            try:
                await update.message.reply_text(f"𝒜𝐿𝐿 𝐿𝐼𝒩𝒦𝒮 𝒟𝒪𝒲𝒩𝐿𝒪𝒜𝒟𝐸𝒟 𝒮𝒰𝒞𝒞𝐸𝒮𝒮𝐹𝒰𝐿𝐿𝒴 ✅", reply_to_message_id=link_msg.id)
            except:
                await update.message.reply_text("**𝒜𝐿𝐿 𝐿𝐼𝒩𝒦𝒮 𝒟𝒪𝒲𝒩𝐿𝒪𝒜𝒟𝐸𝒟 𝒮𝒰𝒞𝒞𝐸𝒮𝒮𝐹𝒰𝐿𝐿𝒴 ✅**")

    async def send_video(self, bot, update, file, thumbnail_filename, msg):
        user_id = update.from_user.id
        if thumbnail_filename:
            await bot.send_video(
                chat_id=user_id,
                video=file,
                thumb=thumbnail_filename,
                caption=f"**📁 File Name:- `{file}`\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}",
                progress=progress_for_pyrogram,
                progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time())
            )
            os.remove(thumbnail_filename)
        else:
            await bot.send_video(
                chat_id=user_id,
                video=file,
                caption=f"**📁 File Name:- `{file}`\n\nHere Is your Requested Video 🔥**\n\nPowered By - @{Config.BOT_USERNAME}",
                progress=progress_for_pyrogram,
                progress_args=("\n⚠️ Please Wait...\n\n**Uploading Started...**", msg, time.time())
            )
        os.remove(file)

downloader = Downloader()

@Client.on_message(filters.regex(pattern=r"(?=.*https://)(?!.*\bmega\b).*") & filters.user(Config.ADMIN))
async def handle_yt_dl(bot: Client, cmd: Message):
    await cmd.reply_text("**Do you want to download this file ?**", reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔻 Download 🔻', callback_data='http_link')], [InlineKeyboardButton('🖇️ Add Multiple Links 🖇️', callback_data='multiple_http_link')]]))

@Client.on_callback_query(filters.regex('^http_link'))
async def handle_single_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text
    await ytdl_downloads(bot, update, http_link)

@Client.on_callback_query(filters.regex('^multiple_http_link'))
async def handle_multiple_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text

    user_id = update.from_user.id
    try:
        if user_id not in downloader.queue_links:
            downloader.queue_links.update({user_id: [http_link]})
            await update.message.delete()
            while True:
                link = await bot.ask(chat_id=user_id, text="🔗Send Link to add it to queue 🔗\n\nUse /done when you're done adding links to queue.", filters=filters.text, reply_to_message_id=update.message.id)

                if str(link.text).startswith("https"):
                    downloader.queue_links[user_id].append(link.text)
                    await update.message.reply_text("Successfully Added To Queue ✅", reply_to_message_id=link.id)
                elif link.text == "/done":
                    user = downloader.queue_links[user_id]
                    links = ""
                    for idx, link in enumerate(user):
                        links += f"{(idx+1)}. `{link}`\n"

                    links_msg = await update.message.reply_text(f"👤 <code>{update.from_user.first_name}</code> 🍁\n\n {links}")
                    break
                else:
                    await update.message.reply_text("⚠️ Please Send Valid Link !")
                    continue

        await update.message.reply_text("Downloading Started ✅\n\nPlease have patience while it's downloading it may take sometimes...")

        if user_id in downloader.queue_links:
            try:
                await downloader.download_multiple(bot, update, links_msg)
            except Exception as e:
                print('Error on line {}'.format(
                    sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


# Progress Hook Function
def download_progress_hook(d, msg, link):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            msg.edit(f"**Downloading {link}\n\nProgress: {percent:.2f}%**")
        elif 'total_bytes_estimate' in d:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            msg.edit(f"**Downloading {link}\n\nProgress: {percent:.2f}%**")
    elif d['status'] == 'finished':
        msg.edit(f"**Downloaded {link}\n\nProcessing...**")


# Progress Function for Pyrogram
def progress_for_pyrogram(current, total, message, start_time):
    elapsed_time = time.time() - start_time
    percentage = current * 100 / total
    speed = current / elapsed_time
    time_to_completion = (total - current) / speed
    estimated_total_time = elapsed_time + time_to_completion

    progress = "[{0}{1}] {2}%\n".format(
        ''.join(["█" for _ in range(math.floor(percentage / 10))]),
        ''.join(["░" for _ in range(10 - math.floor(percentage / 10))]),
        round(percentage, 2))

    tmp = progress + \
        "**Downloaded:** `{0} of {1}`\n**Speed:** `{2}/s`\n**ETA:** `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_formatter(estimated_total_time)
        )
    asyncio.run(message.edit(text=tmp))

def humanbytes(size):
    # Convert bytes to a human readable format
    if not size:
        return ""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KiB', 2: 'MiB', 3: 'GiB', 4: 'TiB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}"

def time_formatter(seconds: int) -> str:
    # Convert seconds to a human readable format
    result = ''
    v_m = seconds // 60
    v_s = seconds % 60
    v_h = v_m // 60
    v_m = v_m % 60
    if v_h != 0:
        result += f"{v_h}h "
    if v_m != 0:
        result += f"{v_m}m "
    result += f"{v_s}s"
    return result
