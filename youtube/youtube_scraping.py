import yt_dlp
import os

# Function to download video and save its basic info
def download_video_and_save_info(url, output_dir, info_file):
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),  # Save video to specified directory
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video information but don't download the video yet
        info = ydl.extract_info(url, download=True)

        # Write the basic video info to the text file
        with open(info_file, 'a', encoding='utf-8') as f:
            f.write(f"Title: {info.get('title', 'N/A')}\n")
            f.write(f"Uploader: {info.get('uploader', 'N/A')}\n")
            f.write(f"Duration: {info.get('duration', 'N/A')} seconds\n")
            f.write(f"View count: {info.get('view_count', 'N/A')}\n")
            f.write(f"URL: {url}\n")
            f.write("-" * 40 + "\n")

# Main function to process the list of URLs
def process_video_list(url_list_file, output_dir, info_file):
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the list of URLs from the file
    with open(url_list_file, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    # Process each URL
    for url in urls:
        try:
            print(f"Downloading and processing: {url}")
            download_video_and_save_info(url, output_dir, info_file)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    # Define input and output files
    url_list_file = 'video_urls.txt'  # File containing a list of video URLs (one URL per line)
    output_dir = 'downloaded_videos'  # Directory to save downloaded videos
    info_file = 'video_info.txt'      # File to save video metadata

    # Start processing the video list
    process_video_list(url_list_file, output_dir, info_file)
