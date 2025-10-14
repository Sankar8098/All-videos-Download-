import os
import time
import re

id_pattern = re.compile(r'^.\d+$')

class Config(object):
    # Pyrogram client config
    API_ID = os.environ.get("API_ID", "23990433")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "e6c4b6ee1933711bc4da9d7d17e1eb20")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6237026610:AAG5iFdJqL6Mm5RX6ACZIueCJJPXpAwqv44")  # ⚠️ Required
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "autofilter2_bot")  # ⚠️ Required
    
    # Database config
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://sankar:sankar@sankar.lldcdsx.mongodb.net/?retryWrites=true&w=majority")  # ⚠️ Required
    
    # Other configs
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    TG_MAX_SIZE = 2040108421
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '5821871362').split()]  # ⚠️ Required
    FORCE_SUB_TEXT = os.environ.get('FORCE_SUB_TEXT', "**You are not in our backup channel given below so you don't get the file...\n\nIf you want the file, click on the '❆ Join Our Backup Channel ❆' button below and join our backup channel, then click on the '↻ Try Again' button below...\n\nThen you will get the files...**")
    FORCE_SUB = os.environ.get('FORCE_SUB', 'SK_MoviesOffl')  # ⚠️ Required
    AUTH_CHANNEL = -1001811608554  # Updated AUTH_CHANNEL value
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001870015374"))  # ⚠️ Required
    
    # Mega User Account ⚠️ Only Set When you have Pro or Enterprise Mega Account
    MEGA_EMAIL = os.environ.get("MEGA_EMAIL", None)
    MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD", None)
    
    # Web response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8081"))

class Txt(object):
    # Part of text configuration
    START_TXT = """<b>Hello {} 👋,
━━━━━━━━━━━━━━━━━━━━━
This Bot Can Search PornHub
Videos & Download Them For You

Can Also Download Files through
Link of Mega & YouTube
━━━━━━━━━━━━━━━━━━━━━
⚠️The Bot Contains 18+ Content
So Kindly Access it with Your own
Risk. Children Please Stay Away.
We don't intend to spread Pørno-
graphy here. It's just a bot for a
purpose as many of them wanted.
━━━━━━━━━━━━━━━━━━━━━
Click The Buttons Below To Search
"""

    ABOUT_TXT = """<b>╭───────────⍟
├🤖 My name : {}
├👨‍💻 Programmer : <a href="https://t.me/Snowball_Official">𝓢𝓝𝓞𝓦𝓑𝓐𝓛𝓛</a>
├👑 Instagram : <a href="https://www.instagram.com/ritesh6_">C-Insta</a>
├☃️ Founder of : <a href="https://t.me/+HzGpLAZXTxoyYTNl">𝖱𝖮𝖮𝖥𝖨𝖵𝖤𝖱𝖲𝖤</a>
├📕 Library : <a href="https://github.com/pyrogram">Pyrogram</a>
├✏️ Language: <a href="https://www.python.org">Python 3</a>
├💾 Database: <a href="https://cloud.mongodb.com">Mongo DB</a>
├🌀 My Server : <a href="https://dashboard.heroku.com">Heroku</a>
╰───────────────⍟ """

    HELP_TXT = """
This Bot Will Help You To Download Following Files Through Links:

⊚ YouTube
⊚ Mega
⊚ PornHub

❗ Any Other Help Contact :- <a href="https://t.me/Snowball_official">Support</a>
"""

    PROGRESS_BAR = """<b>\n
╭━━━━❰Progress Bar❱━➣
┣⪼ 🗃️ Size: {1} | {2}
┣⪼ ⏳️ Done : {0}%
┣⪼ 🚀 Speed: {3}/s
┣⪼ ⏰️ ETA: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""
