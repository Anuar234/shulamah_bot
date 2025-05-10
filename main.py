from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import asyncio
from dotenv import load_dotenv
import aiohttp
import yt_dlp
from yt_dlp.utils import DownloadError
import concurrent.futures
import random

# Load .env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
BOT_USERNAME: Final = '@shulamah_info_bot'

# --- Commands ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your helpful bot 😊")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ask me something or use /download [YouTube URL] to get a video!")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Custom functionality is under construction!")

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Here's something random!")

async def glazer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("You're doing great today! Keep it up!")

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                fact = data.get("text", "Couldn't fetch a fact.")
        await update.message.reply_text(f"🧠 Random Fact:\n{fact}")
    except Exception as e:
        print("Error fetching fact:", e)
        await update.message.reply_text("Failed to fetch a random fact.")

# --- Video Download ---
async def download_video(url, ydl_opts, timeout=600):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        try:
            def _download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    return ydl.prepare_filename(info)
            return await asyncio.wait_for(loop.run_in_executor(pool, _download), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError("yt-dlp timed out")

async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample:\n/download https://youtube.com/...")
        return

    url = context.args[0]
    await update.message.reply_text("Downloading video... ⏳")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'prefer_ffmpeg': True,
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        file_path = await download_video(url, ydl_opts)
        file_size = os.path.getsize(file_path)

        if file_size > 300 * 1024 * 1024:
            await update.message.reply_text("⚠️ Video is too large to send via Telegram (max 300MB).")
            os.remove(file_path)
            return

        with open(file_path, 'rb') as f:
            await update.message.reply_video(video=f)

        os.remove(file_path)
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ Download timed out. Try a different link or shorter video.")
    except DownloadError as e:
        await update.message.reply_text(f"❌ Download error: {e}")
    except Exception as e:
        print("Unexpected error:", e)
        await update.message.reply_text("⚠️ An unexpected error occurred.")


# --- Text Message Handler ---
def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hi there!'
    if 'what' in processed:
        return 'What can I help you with?'
    if 'anuar' in processed:
        return 'You mean the GOAT Anuar?'
    if 'ibra' in processed:
        return 'boss kfc'
    if 'surik' in processed:
        return 'chinese nigga'
    if 'aldik' in processed:
        return 'main mongol'
    return 'Try saying "hello", "what", or a name like "Anuar".'

async def random_local_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_path = "downloads"  # path to your image folder
    try:
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            await update.message.reply_text("No images found in the folder.")
            return

        random_file = random.choice(image_files)
        file_path = os.path.join(folder_path, random_file)

        with open(file_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="🖼 Random PRIVET picture")

    except Exception as e:
        print("Error sending local image:", e)
        await update.message.reply_text("Something went wrong while sending the image.")


# --- Voice Handler ---
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(process_voice(update, context))
    await update.message.reply_text("Processing your voice message... 🎙️")

# Voice message handler
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔊 Listening...")

    file = await update.message.voice.get_file()
    ogg_path = "temp.ogg"
    wav_path = "temp.wav"
    text_path = "temp.txt"
    mp3_path = "voice.mp3"

    try:
        await file.download_to_drive(ogg_path)

        # Convert OGG to WAV
        sound = AudioSegment.from_file(ogg_path)
        sound.export(wav_path, format="wav")

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        # Try Russian first, then English
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")
        except sr.UnknownValueError:
            text = recognizer.recognize_google(audio_data, language="en-US")

        print("Recognized text:", text)

        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Speak the text back
        tts = gTTS(text=text, lang="en")
        tts.save(mp3_path)

        await update.message.reply_voice(voice=open(mp3_path, "rb"))

    except sr.UnknownValueError:
        await update.message.reply_text("❌ Couldn't understand audio.")
    except sr.RequestError as e:
        await update.message.reply_text(f"⚠️ Google API error: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Unexpected error: {e}")
    finally:
        # Clean up
        for f in [ogg_path, wav_path, text_path, mp3_path]:
            if os.path.exists(f):
                os.remove(f)

async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file_id = voice.file_id
    ogg_path = "voice_message.ogg"
    wav_path = "voice_message.wav"
    mp3_path = "response.mp3"

    try:
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(ogg_path)

        audio = AudioSegment.from_file(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = None
        lang = None

        # Try Russian
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            lang = "ru"
        except sr.UnknownValueError:
            print("Russian not recognized, trying English...")

        # Try English if Russian fails
        if not text:
            try:
                text = recognizer.recognize_google(audio_data, language="en-US")
                lang = "en"
            except sr.UnknownValueError:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't understand that in either Russian or English.")
                return

        if text:
            print(f"Recognized ({lang.upper()}): {text}")
            reply_text = "Ты сказал: " + text if lang == "ru" else "You said: " + text
            tts = gTTS(text=reply_text, lang=lang)
            tts.save(mp3_path)

            with open(mp3_path, 'rb') as audio_file:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=audio_file)

    except sr.RequestError as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Google API error: {e}")
    except Exception as e:
        print("Processing error:", e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while processing your voice message.")
    finally:
        for path in [ogg_path, wav_path, mp3_path]:
            if os.path.exists(path):
                os.remove(path)


    voice = update.message.voice
    file_id = voice.file_id
    ogg_path = "voice.ogg"
    wav_path = "voice.wav"
    mp3_path = "response.mp3"

    try:
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(ogg_path)

        audio = AudioSegment.from_file(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = None
        lang = None

        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            lang = "ru"
        except sr.UnknownValueError:
            print("Russian not recognized")

        if not text:
            try:
                text = recognizer.recognize_google(audio_data, language="en-US")
                lang = "en"
            except sr.UnknownValueError:
                await update.message.reply_text("Sorry, couldn't understand your voice message.")
                return

        if text:
            print(f"Recognized ({lang}): {text}")
            reply_text = "Ты сказал: " + text if lang == "ru" else "You said: " + text
            tts = gTTS(text=reply_text, lang=lang)
            tts.save(mp3_path)

            with open(mp3_path, 'rb') as f:
                await update.message.reply_voice(voice=f)

    except sr.RequestError as e:
        await update.message.reply_text(f"Speech recognition error: {e}")
    except Exception as e:
        print("Voice processing error:", e)
        await update.message.reply_text("Failed to process voice.")
    finally:
        for path in [ogg_path, wav_path, mp3_path]:
            if os.path.exists(path):
                os.remove(path)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_type = update.message.chat.type

    if chat_type == 'group' and BOT_USERNAME not in text:
        return

    new_text = text.replace(BOT_USERNAME, '').strip() if BOT_USERNAME in text else text
    response = handle_response(new_text)
    await update.message.reply_text(response)

# --- Error Handler ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

# --- Main ---
if __name__ == '__main__':
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


    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Errors
    app.add_error_handler(error_handler)

    print("Bot is polling...")
    app.run_polling(poll_interval=3)
