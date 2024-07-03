import logging
import logging.config
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from pytz import timezone
from datetime import datetime
from plugins.web_support import web_server
import pyromod
import asyncio

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


class Bot(Client):

    def __init__(self):
        super().__init__(
            name="Snowball",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.stop_event = asyncio.Event()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, Config.PORT).start()
        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

        for id in Config.ADMIN:
            try:
                await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
            except Exception as e:
                logging.error(f"Failed to send start message to admin: {e}")

        if Config.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time = curr.strftime('%I:%M:%S %p')
                await self.send_message(Config.LOG_CHANNEL, f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n📅 Dᴀᴛᴇ : `{date}`\n⏰ Tɪᴍᴇ : `{time}`\n🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`</b>")
            except Exception as e:
                logging.error(f"Please make sure this bot is an admin in your log channel: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

    async def run(self):
        await self.start()
        await self.stop_event.wait()


async def main():
    bot = Bot()
    await bot.run()

if __name__ == "__main__":
    # Ensure that the asyncio event loop is used consistently
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
