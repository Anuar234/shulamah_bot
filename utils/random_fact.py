import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                fact = data.get("text", "Couldn't fetch a fact.")
        await update.message.reply_text(f"\U0001F9E0 Random Fact:\n{fact}")
    except Exception as e:
        print("Error fetching fact:", e)
        await update.message.reply_text("Failed to fetch a random fact.")
