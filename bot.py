import os
import yt_dlp
from telethon import TelegramClient, events

# Telegram API credentials
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

# Initialize the Telethon client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Function to download YouTube video using yt-dlp with cookies for authentication
def download_youtube_video(url):
    try:
        # yt-dlp options with cookies for authentication
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Best quality video and audio
            'outtmpl': '%(title)s.%(ext)s',        # Name the file after the video title
            'merge_output_format': 'mp4',          # Merge into an mp4 file
            'cookies': '/cookies.txt'       # Path to the cookies.txt file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict)
        return video_file
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Handler to listen for messages containing YouTube URLs
@client.on(events.NewMessage(pattern=r'https?://(www\.)?(youtube|youtu\.be)\.com/watch\?v=.+'))
async def youtube_download_handler(event):
    youtube_url = event.text.strip()
    sender = await event.get_sender()

    # Notify the user that download has started
    await event.reply("Downloading your video... Please wait!")

    # Download the video
    video_file = download_youtube_video(youtube_url)
    
    if video_file and os.path.exists(video_file):
        # Notify the user that the download is complete
        await event.reply(f"Download complete. Uploading video to chat...")

        # Upload the video to Telegram
        await client.send_file(event.chat_id, video_file, caption="Here is your video!")

        # Clean up the video file after sending
        os.remove(video_file)
    else:
        await event.reply("Sorry, there was an error downloading the video.")

# Start the bot
print("Bot is running...")
client.run_until_disconnected()
