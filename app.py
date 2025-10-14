from flask import Flask
from threading import Thread
from bot import start_bot
import asyncio

app = Flask(__name__)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

@app.route('/')
def hello_world():
    return 'Bot is running!'

@app.route('/healthz')
def healthz():
    return 'OK'

if __name__ == "__main__":
    thread = Thread(target=run_bot)
    thread.start()
    app.run(host='0.0.0.0', port=8080)