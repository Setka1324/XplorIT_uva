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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Define the scope for accessing Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Get credentials and API keys from environment variables
SHEET_ID = "1FwOu_RssRJ7teP5NGzmenXIRAKgsOXoP4dbOBjFqN0k"
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
    


# Define a function to perform sentiment analysis and calculate the positivity score
def get_sentiment(text):
    if text.strip():  # Check if text is not empty
        sentiment = analyzer.polarity_scores(text)
        compound_score = sentiment['compound']  # Get the compound score
        return compound_score
    return 0  # Return neutral score for empty text

def update_positivity_for_existing_rows_from_empty():
    """
    Update positivity scores for rows starting from those with empty positivity cells.
    """
    rows = sheet.get_all_values()
    header = rows[0]
    data = rows[1:]

    # Check if 'positivity' column exists
    if "positivity" not in header:
        # Add 'positivity' column to the header
        header.append("positivity")
        sheet.update_cell(1, len(header), "positivity")  # Add column header to Google Sheet

    # Get the column indexes
    transcribed_text_col = header.index("Transcribed text") + 1
    positivity_col = header.index("positivity") + 1

    for i, row in enumerate(data, start=2):  # Start from the second row
        try:
            positivity_value = row[positivity_col - 1] if len(row) >= positivity_col else ""
            if not positivity_value.strip():  # Check if positivity is empty
                transcribed_text = row[transcribed_text_col - 1]  # Fetch Transcribed text
                positivity_score = get_sentiment(transcribed_text)
                
                # Update the positivity column in Google Sheets
                sheet.update_cell(i, positivity_col, positivity_score)
                print(f"Updated positivity score for row {i}: {positivity_score}")
        except IndexError:
            print(f"Error processing row {i}: {row}")


def update_positivity_for_new_row():
    """
    Update the positivity score for the most recently added row.
    """
    # Get all rows from the sheet
    rows = sheet.get_all_values()

    # Separate header and data
    header = rows[0]
    data = rows[1:]

    # Get the column indexes
    if "positivity" not in header:
        print("Positivity column not found. Run update_positivity_for_existing_rows first.")
        return

    transcribed_text_col = header.index("Transcribed text") + 1
    positivity_col = header.index("positivity") + 1

    # Process the last row
    last_row_index = len(data) + 1
    transcribed_text = data[-1][transcribed_text_col - 1]  # Fetch Transcribed text
    positivity_score = get_sentiment(transcribed_text)
    
    # Update the positivity column for the last row
    sheet.update_cell(last_row_index, positivity_col, positivity_score)
    print(f"Updated positivity score for the last row: {positivity_score}")




# Main function
def main(video_link):
    if video_exists(sheet, video_link):
        print("Video already exists in the sheet.")
    else:
        title, date_posted, youtuber, length = get_video_info(video_link)
        if title and date_posted and youtuber and length:
            transcript = transcribe_video(video_link)
            
            # Append new row to the sheet
            sheet.append_row([video_link, "", transcript, title, date_posted, youtuber, "", "", length, ""])
            print("Video information and transcription added to the sheet.")

            # Update positivity score for the new row
            update_positivity_for_new_row()
        else:
            print("Failed to retrieve video information.")

#update_positivity_for_existing_rows_from_empty()

# Example usage
video_link = input("Enter YouTube video link: ")
main(video_link)
