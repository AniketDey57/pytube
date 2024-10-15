import os
import yt_dlp
from telethon import TelegramClient, events
import google_auth_oauthlib.flow
import google.auth.transport.requests
import google.oauth2.credentials

# Telegram API credentials
api_id = '15076648'
api_hash = '7a6e491475ab66bf5097a8a2f295ac98'
bot_token = '5707293090:AAHGLlHSx101F8T1DQYdcb9_MkRAjyCbt70'

# Google OAuth 2.0 Client Secret JSON file
client_secrets_file = 'client_secret.json'  # Path to your OAuth 2.0 credentials

# Initialize the Telethon client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Function to get OAuth credentials
def get_google_oauth_credentials():
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    
    credentials = flow.run_local_server(port=0)
    return credentials

# Function to download YouTube video using yt-dlp with OAuth credentials
def download_youtube_video(url, credentials):
    try:
        # yt-dlp options with OAuth credentials for authentication
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Best quality video and audio
            'outtmpl': '%(title)s.%(ext)s',        # Name the file after the video title
            'merge_output_format': 'mp4',          # Merge into an mp4 file
            'http_headers': {
                'Authorization': f'Bearer {credentials.token}'
            }
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

    # Get OAuth credentials from Google
    credentials = get_google_oauth_credentials()

    # Download the video
    video_file = download_youtube_video(youtube_url, credentials)
    
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
