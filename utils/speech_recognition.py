import speech_recognition as sr
from gtts import gTTS
from telegram import Update
from telegram.ext import ContextTypes
import os
from pydub import AudioSegment 

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
