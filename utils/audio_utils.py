import random
import os
from telegram import Update
from telegram.ext import ContextTypes
import asyncio
import concurrent.futures
import yt_dlp
from yt_dlp.utils import DownloadError


async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL.\nExample:\n/audio https://youtube.com/...")
        return

    url = context.args[0]
    await update.message.reply_text("Downloading audio... 🎶")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/audios/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    async def download_video(url, ydl_opts, timeout=600):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                def _download():
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        base, _ = os.path.splitext(filename)
                        return base + '.mp3'
                return await asyncio.wait_for(loop.run_in_executor(pool, _download), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError("yt-dlp timed out")

    try:
        os.makedirs("downloads/audios", exist_ok=True)
        file_path = await download_video(url, ydl_opts)
        if not os.path.exists(file_path):
            await update.message.reply_text("Audio file not found after processing.")
            return

        with open(file_path, 'rb') as f:
            await update.message.reply_audio(audio=f)

        os.remove(file_path)
    except asyncio.TimeoutError:
        await update.message.reply_text("⏳ Download timed out. Try a different link or shorter video.")
    except DownloadError as e:
        await update.message.reply_text(f"❌ Download error: {e}")
    except Exception as e:
        print("Unexpected error:", e)
        await update.message.reply_text("⚠️ An unexpected error occurred.")




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
