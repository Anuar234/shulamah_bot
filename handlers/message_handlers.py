from telegram import Update
from telegram.ext import ContextTypes
import random
import os
from utils.audio_utils import download_audio, random_local_image
from utils.speech_recognition import handle_voice_message
from utils.random_fact import random_fact
from telegram.ext import MessageHandler, filters
from pydub import AudioSegment
import os
import speech_recognition as sr
from gtts import gTTS
from config import BOT_USERNAME

from gtts import gTTS
def handle_response(text: str) -> str:
    processed = text.lower()
    responses = {
        'hello': 'Hi there!',
        'what': 'What can I help you with?',
        'anuar': 'You mean the GOAT Anuar?',
        'ibra': 'boss kfc',
        'surik': 'chinese nigga',
        'aldik': 'main mongol'
    }
    for keyword, response in responses.items():
        if keyword in processed:
            return response
    return 'Try saying "hello", "what", or a name like "Anuar".'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if update.message.chat.type == 'group' and context.bot.username not in text:
        return
    new_text = text.replace(context.bot.username, '').strip() if context.bot.username in text else text
    await update.message.reply_text(handle_response(new_text))

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Processing your voice message... 🎙️")
    await process_voice(update, context)

async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    ogg_path, wav_path, mp3_path = "temp.ogg", "temp.wav", "response.mp3"

    try:
        await file.download_to_drive(ogg_path)
        AudioSegment.from_file(ogg_path).export(wav_path, format="wav")
        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text, lang = None, None
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            lang = "ru"
        except sr.UnknownValueError:
            try:
                text = recognizer.recognize_google(audio_data, language="en-US")
                lang = "en"
            except sr.UnknownValueError:
                await update.message.reply_text("❌ Couldn't understand audio.")
                return

        if text:
            reply_text = "Ты сказал: " + text if lang == "ru" else "You said: " + text
            gTTS(text=reply_text, lang=lang).save(mp3_path)
            with open(mp3_path, 'rb') as audio:
                await update.message.reply_voice(voice=audio)

    except sr.RequestError as e:
        await update.message.reply_text(f"⚠️ Google API error: {e}")
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