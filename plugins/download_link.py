import asyncio
import os
import sys
import time
import uuid
import math
import requests
import moviepy
from moviepy.editor import VideoFileClip
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import youtube_dl
from config import Config
from helper.utils import (
    get_thumbnail_url,
    get_porn_thumbnail_url  # Assuming you have implemented this function in your helper module
)

class Downloader:
    def __init__(self):
        self.queue_links = {}

    async def download_multiple(self, bot, update, link_msg, index=0):
        user_id = update.from_user.id
        msg = await update.message.reply_text(
            f"**{index+1}. Link:-** {self.queue_links[user_id][index]}\n\nDownloading... Please Have Patience\nLoading...",
            disable_web_page_preview=True
        )

        ytdl_opts = {
            'format': 'best',
            'progress_hooks': [lambda d: download_progress_hook(d, msg, self.queue_links[user_id][index])]
        }

        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(self.queue_links[user_id][index], download=False)
                video_url = info_dict.get("url", None)
                ydl.download([self.queue_links[user_id][index]])
            except youtube_dl.utils.DownloadError as e:
                await msg.edit(f"Sorry, There was a problem with that particular video: {e}")
                index += 1
                if index < len(self.queue_links[user_id]):
                    await self.download_multiple(bot, update, link_msg, index)
                else:
                    await update.message.reply_text("All Links Downloaded Successfully ✅", reply_to_message_id=link_msg.id)
                return

        unique_id = uuid.uuid4().hex
        thumbnail_filename = None
        if thumbnail:
            thumbnail_filename = f"thumbnail_{unique_id}.jpg"
            response = requests.get(thumbnail)
            if response.status_code == 200:
                with open(thumbnail_filename, 'wb') as f:
                    f.write(response.content)

        await msg.edit("Uploading...")

        video_file = f"{user_id}_{index}.mp4"
        os.rename(info_dict['id'], video_file)

        try:
            await self.send_video(bot, update, video_file, thumbnail_filename, msg, info_dict['duration'])
        except Exception as e:
            print("Error sending video:", e)

        await msg.delete()

        index += 1
        if index < len(self.queue_links[user_id]):
            await self.download_multiple(bot, update, link_msg, index)
        else:
            await update.message.reply_text("All Links Downloaded Successfully ✅", reply_to_message_id=link_msg.id)

    async def send_video(client, file_path, thumbnail_path, video_title, reply_msg, collection_channel_id, user_mention, user_id, message):
    file_size = os.path.getsize(file_path)
    uploaded = 0
    start_time = datetime.now()
    last_update_time = time.time()

    try:
        duration = 0
        path = str(file_path)
        clip = VideoFileClip(path)
        duration = int(clip.duration)
        clip.close()
    except Exception as e:
        logging.warning(f"can't add duration: {e}")
        duration = 0
        
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    conv_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
            os.remove(thumbnail_filename)  # Remove the temporary thumbnail file after upload
        else:
            await bot.send_video(
                chat_id=user_id,
                video=video_file,
                caption=f"Video Name: `{video_file}`\n\nRequested Video",
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=(msg, time.time())
            )
        os.remove(video_file)  # Remove the downloaded video file after upload

downloader = Downloader()

@Client.on_message(filters.regex(pattern=r"(?=.*https://)(?!.*\bmega\b).*") & filters.user(Config.ADMIN))
async def handle_yt_dl(bot: Client, cmd: Message):
    await cmd.reply_text("Do you want to download this file?", reply_to_message_id=cmd.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔻 Download 🔻', callback_data='http_link')], [InlineKeyboardButton('🖇️ Add Multiple Links 🖇️', callback_data='multiple_http_link')]]))

@Client.on_callback_query(filters.regex('^http_link'))
async def handle_single_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text
    await ytdl_downloads(bot, update, http_link)  # Assuming ytdl_downloads handles single link downloads

@Client.on_callback_query(filters.regex('^multiple_http_link'))
async def handle_multiple_download(bot: Client, update: CallbackQuery):
    http_link = update.message.reply_to_message.text

    user_id = update.from_user.id
    try:
        if user_id not in downloader.queue_links:
            downloader.queue_links[user_id] = []
            downloader.queue_links[user_id].append(http_link)
            await update.message.delete()
            while True:
                link = await bot.ask(
                    chat_id=user_id,
                    text="Send Link to add it to queue",
                    filters=filters.text,
                    reply_to_message_id=update.message.message_id
                )

                if str(link.text).startswith("https"):
                    downloader.queue_links[user_id].append(link.text)
                    await link.reply_text("Successfully Added To Queue ✅")
                elif link.text == "/done":
                    user = downloader.queue_links[user_id]
                    links = ""
                    for idx, link in enumerate(user):
                        links += f"{(idx+1)}. `{link}`\n"

                    links_msg = await update.message.reply_text(f"{links}")
                    break
                else:
                    await link.reply_text("Please Send Valid Link !")
                    continue

        await update.message.reply_text("Downloading Started ✅")

        if user_id in downloader.queue_links:
            await downloader.download_multiple(bot, update, links_msg)

    except Exception as e:
        print('Error:', e)

# Progress Hook Function
def download_progress_hook(d, msg, link):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            msg.edit(f"Downloading {link}\nProgress: {percent:.2f}%")
        elif 'total_bytes_estimate' in d:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            msg.edit(f"Downloading {link}\nProgress: {percent:.2f}%")
    elif d['status'] == 'finished':
        msg.edit(f"Downloaded {link}\nProcessing...")

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
        "Downloaded: `{0} of {1}`\nSpeed: `{2}/s`\nETA: `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_formatter(estimated_total_time)
        )
    asyncio.run(message.edit(text=tmp))

def humanbytes(size):
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
