from typing import Final
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes 
import os
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import asyncio
from dotenv import load_dotenv
import aiohttp
import yt_dlp
# Load the environment variables from the .env file
load_dotenv()

# Now, load the token from the environment variable
TOKEN = os.getenv("TOKEN")
BOT_USERNAME: Final = '@shulamah_info_bot'



# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Shut yo bitch ass up!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Let yo ass ask something from me, cause I want to help you')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Wanna custom things? Do ts shi') 

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('3 niggers gonna fuck u tonight')

async def glazer_commad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('u such a wonderful nigga')

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://uselessfacts.jsph.pl/random.json?language=en"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                fact = data.get("text", "Could not get a fact right now.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🧠 Random Fact:\n{fact}")
    
    except Exception as e:
        print("error fethcing fact:", e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Something went wrong while fetching a fact.")


async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample:\n/download https://youtube.com/...")
        return

    url = context.args[0]
    await update.message.reply_text("Downloading video... Please wait ⏳")

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Check file size (Telegram limit = 2GB)
        file_size = os.path.getsize(file_path)
        if file_size > 2 * 1024 * 1024 * 1024:
            await update.message.reply_text("Video is too large to send via Telegram.")
            os.remove(file_path)
            return

        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)

        os.remove(file_path)

    except Exception as e:
        print("Download error:", e)
        await update.message.reply_text(f"Error downloading video: {e}")


# Handle Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()


    if 'hello' in processed:
        return 'Nigga stfu'
    
    if 'what' in processed:
        return 'get yo fucking ass out ts chat'
    
    if 'anuar' in processed:
        return 'you mean THE GOAT?'
    if 'surik' in processed:
        return 'ohh thats chinese kotakbas'
    if 'alpa' in processed:
        return 'thats a cobalt of privet '
    if 'nura' in processed:
        return 'oh you mean woody from Toy Story?'
    if 'ibra' in processed:
        return 'sektant'
    if 'aldik' in processed:
        return 'main mongol'
    if 'suka' in processed:
        return 'che ahuel suka'
    if 'anus' in processed:
        return 'иди нахуй'
    
    return 'write "hello", "what", "surik" "ibra", "nura" , "alpa", "aldik", "anuar" to that '


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user = update.message.from_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name

    print(f"User ID: {user_id}")
    print(f"Username: @{username}")
    print(f"First name: {first_name}")
    print(f"Last name: {last_name}")


    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')


    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strp()
            response: str = handle_response(new_text)
        else:
            return 
    else:
        response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(process_voice(update, context))
    await update.message.reply_text("Listening yo shi")

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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    
    #commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('random', random_command))
    app.add_handler(CommandHandler('glazer', glazer_commad))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(CommandHandler("random_fact", random_fact))
    app.add_handler(CommandHandler("download", download_command))



    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))


    # errors
    app.add_error_handler(error_handler)


    #polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)