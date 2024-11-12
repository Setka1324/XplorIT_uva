import os
from moviepy.editor import VideoFileClip

def extract_audio_from_mp4(mp4_path, mp3_path):
    try:
        video = VideoFileClip(mp4_path)
        audio = video.audio
        if audio is not None:
            audio.write_audiofile(mp3_path, logger=None)
            print(f"Extracted: {mp3_path}")
        else:
            print(f"No audio found in: {mp4_path}")
        video.close()
    except Exception as e:
        print(f"Failed to extract audio from {mp4_path}. Error: {e}")

def traverse_and_extract(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.mp4'):
                mp4_path = os.path.join(dirpath, filename)
                mp3_filename = os.path.splitext(filename)[0] + '.mp3'
                mp3_path = os.path.join(dirpath, mp3_filename)
                
                # Check if mp3 already exists to avoid re-processing
                if not os.path.exists(mp3_path):
                    extract_audio_from_mp4(mp4_path, mp3_path)
                else:
                    print(f"MP3 already exists: {mp3_path}")

def main():
    # List of your main folders
    main_folders = ['General', 'Our challenge', 'Our Xplorations']
    
    # Get the current working directory
    cwd = os.getcwd()
    
    for folder in main_folders:
        folder_path = os.path.join(cwd, folder)
        if os.path.isdir(folder_path):
            print(f"Processing folder: {folder_path}")
            traverse_and_extract(folder_path)
        else:
            print(f"Folder not found: {folder_path}")

if __name__ == "__main__":
    main()
