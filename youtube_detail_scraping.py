import gspread
import requests
from google.oauth2.service_account import Credentials
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import speech_recognition as sr
from datetime import datetime, timedelta
import re
import whisper
import os

# Define the scope for accessing Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Get credentials and API keys from environment variables
SHEET_ID = "1iHqK6RI2gSuZ7LgLa6zibyj6q7jqScAsIXfTFOV3Hz0"
YOUTUBE_API_KEY= "AIzaSyAbJwYxSCPLhFTQ_MiA51s8O-YWxnA8Kfc"
credentials = Credentials.from_service_account_file("./credentials.json", scopes=SCOPES)

# Authenticate and initialize Google Sheets
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).sheet1

# Check if video exists in the sheet
def video_exists(sheet, video_link):
    links = sheet.col_values(1)  # Assuming 'Link' is in the first column
    return video_link in links

# Convert ISO duration (PT8M47S) to minutes
def convert_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return "Unknown duration"
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    total_minutes = hours * 60 + minutes + (seconds / 60)
    return f"{int(total_minutes)}:{int(seconds):02d}"  # Format as MM:SS

# Convert ISO date (2022-04-17T11:00:11Z) to DD.MM.YYYY
def format_date(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    return date.strftime('%d.%m.%Y')

# Retrieve YouTube video information
def get_video_info(video_link):
    video_id = video_link.split("v=")[-1]
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("items", [])
        if data:
            video_info = data[0]
            title = video_info["snippet"]["title"]
            date_posted = format_date(video_info["snippet"]["publishedAt"])
            youtuber = video_info["snippet"]["channelTitle"]
            length = convert_duration(video_info["contentDetails"]["duration"])
            return title, date_posted, youtuber, length
    return None, None, None, None

# Download and transcribe audio from the video using Whisper
def transcribe_video(video_link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    
    # Download the audio file from the YouTube video
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_link])

    # Check if the audio file exists
    if not os.path.exists("audio.wav"):
        print("Audio file was not created successfully.")
        return "Transcription failed due to missing audio file."

    # Load the Whisper model
    model = whisper.load_model("base")  # Choose model size: "tiny", "base", "small", "medium", "large"

    # Transcribe audio using Whisper
    try:
        result = model.transcribe("audio.wav")
        transcript = result['text']
        return transcript
    except Exception as e:
        print(f"Error during transcription: {e}")
        return "Transcription failed due to Whisper error."

# Main function
def main(video_link):
    if video_exists(sheet, video_link):
        print("Video already exists in the sheet.")
    else:
        title, date_posted, youtuber, length = get_video_info(video_link)
        if title and date_posted and youtuber and length:
            transcript = transcribe_video(video_link)
            sheet.append_row([video_link, "", transcript, title, date_posted, youtuber, "", "", length, ""])
            print("Video information and transcription added to the sheet.")
        else:
            print("Failed to retrieve video information.")

# Example usage
video_link = input("Enter YouTube video link: ")
main(video_link)
