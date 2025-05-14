import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from handlers.command_handlers import start_command, help_command, custom_command, random_command, glazer_command
from handlers.message_handlers import handle_message, handle_voice_message
from config import TOKEN
from utils.audio_utils import random_local_image, download_audio
from utils.download_video import download_command
from utils.random_fact import random_fact
from handlers.message_handlers import error_handler



# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    handlers = [
        ("start", start_command), ("help", help_command), ("custom", custom_command),
        ("random", random_command), ("glazer", glazer_command), ("random_fact", random_fact),
        ("pic", random_local_image), ("audio", download_audio)
    ]
    for cmd, handler in handlers:
        app.add_handler(CommandHandler(cmd, handler))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_error_handler(error_handler)

    print("Bot is polling...")
    app.run_polling(poll_interval=3)
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("random", random_command))
    app.add_handler(CommandHandler("glazer", glazer_command))
    app.add_handler(CommandHandler("random_fact", random_fact))
    app.add_handler(CommandHandler("download", download_command))
    app.add_handler(CommandHandler("pic", random_local_image))
    app.add_handler(CommandHandler("audio", download_audio))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Errors
    app.add_error_handler(error_handler)

    print("Bot is polling...")
    app.run_polling(poll_interval=3)

