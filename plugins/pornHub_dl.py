import asyncio
from pornhub_api import PornhubApi
from pornhub_api.backends.aiohttp import AioHttpBackend
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

# Initialize Pyrogram client
app = Client("my_bot")

# Define inline keyboard buttons
btn1 = InlineKeyboardButton("Search Here", switch_inline_query_current_chat="")
btn2 = InlineKeyboardButton("Go Inline", switch_inline_query="")

# Helper function to format duration
def format_duration(duration):
    try:
        parts = duration.split(':')
        if len(parts) == 2:  # MM:SS
            minutes = int(parts[0])
            seconds = int(parts[1])
            hours = 0
        elif len(parts) == 3:  # HH:MM:SS
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
        else:
            return duration  # Return original if format is unexpected

        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except Exception as e:
        print(f"Error formatting duration: {e}")
        return duration

# Handle inline queries
@app.on_inline_query()
async def search(client, query: InlineQuery):
    query_text = query.query.strip()

    # Check if query is empty
    if not query_text:
        await query.answer([], switch_pm_text="Please enter a search query!", switch_pm_parameter="start")
        return

    backend = AioHttpBackend()
    api = PornhubApi(backend=backend)
    results = []

    try:
        src = await api.search.search(query_text)  # Perform search
    except ValueError:
        # Handle case where no videos are found
        results.append(InlineQueryResultArticle(
            title="No Such Videos Found!",
            description="Sorry! No videos were found for your query.",
            input_message_content=InputTextMessageContent(
                message_text="No videos found!"
            )
        ))
        await query.answer(results, switch_pm_text="Search Results", switch_pm_parameter="start")
        await backend.close()
        return

    videos = src.videos

    for vid in videos:
        try:
            pornstars = ", ".join(vid.pornstars) if vid.pornstars else "N/A"
            categories = ", ".join(vid.categories) if vid.categories else "N/A"
            tags = ", #".join(vid.tags) if vid.tags else "N/A"
        except Exception as e:
            print(f"Error processing video: {e}")
            pornstars = "N/A"
            categories = "N/A"
            tags = "N/A"

        # Format the duration
        formatted_duration = format_duration(vid.duration)

        msg = (f"**TITLE**: `{vid.title}`\n"
               f"**DURATION**: `{formatted_duration}`\n"
               f"**VIEWS**: `{vid.views}`\n\n"
               f"**Pornstars**: {pornstars}\n"
               f"**Categories**: {categories}\n\n"
               f"**Tags**: #{tags}\n"
               f"**Link**: {vid.url}")

        results.append(InlineQueryResultArticle(
            title=vid.title,
            input_message_content=InputTextMessageContent(
                message_text=msg,
                disable_web_page_preview=True
            ),
            description=f"Duration: {formatted_duration}\nViews: {vid.views}\nRating: {vid.rating}",
            thumb_url=vid.thumb,  # Assuming vid.thumb is a valid URL
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Watch Online", url=vid.url), btn1]
            ]),
        ))

    await query.answer(results, switch_pm_text="Search Results", switch_pm_parameter="start")
    await backend.close()

# Start the bot
app.run()
