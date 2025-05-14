from telegram import Update
from spotipy.oauth2 import SpotifyOAuth

from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Wassup, Ima help you to do something w me")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use default command, displayed in this bot through \\")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ima thinking about it, works are still on process")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gives random music to you")

async def glazer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ima glaze you")
