import yt_dlp
from yt_dlp.utils import DownloadError
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import concurrent.futures
import os

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
