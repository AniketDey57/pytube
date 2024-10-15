import os
import pytube
from telethon import TelegramClient, events
from telethon.tl.types import InputMediaUploadedDocument

# Telegram API credentials
api_id = '15076648'
api_hash = '7a6e491475ab66bf5097a8a2f295ac98'
bot_token = '5707293090:AAHGLlHSx101F8T1DQYdcb9_MkRAjyCbt70'

# Create the Telethon client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Function to download YouTube video in highest quality
def download_youtube_video(url):
    try:
        yt = pytube.YouTube(url)
        stream = yt.streams.get_highest_resolution()  # Fetch the highest quality available
        video_file = stream.download()  # Download the video
        return video_file
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Handler to listen for messages containing YouTube URLs
@client.on(events.NewMessage(pattern=r'https?://(www\.)?youtube\.com/watch\?v=.+'))
async def youtube_download_handler(event):
    youtube_url = event.text.strip()
    sender = await event.get_sender()

    # Notify the user that download has started
    await event.reply("Downloading your video... Please wait!")

    # Download the video
    video_file = download_youtube_video(youtube_url)
    
    if video_file:
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
