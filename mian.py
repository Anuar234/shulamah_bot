from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
import os
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import tempfile
import asyncio
from dotenv import load_dotenv
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
    await update.message.reply_text("Processing your voice message...")

async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file_id = voice.file_id
    ogg_path = "voice_message.ogg"
    wav_path = "voice_message.wav"

    try:
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(ogg_path)

        audio = AudioSegment.from_file(ogg_path)
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            print("Recognized:", text)

            # Generate response with gTTS
            tts = gTTS(text="You said: " + text)
            mp3_path = "response.mp3"
            tts.save(mp3_path)

            with open(mp3_path, 'rb') as audio_file:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=audio_file)

            os.remove(mp3_path)
        except sr.UnknownValueError:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't understand that.")
        except sr.RequestError as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Google API error: {e}")

    except Exception as e:
        print("Processing error:", e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while processing your voice message.")

    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

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
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))  # ✅ add voice handler


    #messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))


    # errors
    app.add_error_handler(error_handler)


    #polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)