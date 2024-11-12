import os
import whisper
from tqdm import tqdm
import logging

logging.basicConfig(
    filename='transcription.log',
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_whisper_model(model_size="base"):
    """
    Load the Whisper model.
    Available sizes: tiny, base, small, medium, large
    """
    print(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)
    print("Model loaded successfully.")
    return model

def transcribe_audio(model, mp3_path, language=None):
    try:
        result = model.transcribe(mp3_path, language=language)
        transcription = result['text'].strip()
        logging.info(f"Transcribed {mp3_path}.")
        print(f"Transcription for {os.path.basename(mp3_path)}:\n{transcription}\n")
        return transcription
    except Exception as e:
        logging.error(f"Error transcribing {mp3_path}: {e}")
        return ""


def ensure_directory(path):
    """
    Ensure that a directory exists; if not, create it.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def traverse_and_transcribe(parent_dir, model, language=None):
    # Define your main folders
    main_folders = ['General', 'Our challenge', 'Our Xplorations']
    
    for main_folder in main_folders:
        main_path = os.path.join(parent_dir, main_folder)
        if not os.path.isdir(main_path):
            logging.warning(f"Main folder not found: {main_path}")
            continue
        
        # Iterate through each category in the main folder
        for category in os.listdir(main_path):
            category_path = os.path.join(main_path, category)
            if not os.path.isdir(category_path):
                continue
            
            mp3_folder = os.path.join(category_path, 'mp3')
            transcribed_folder = os.path.join(category_path, 'transcribed')
            ensure_directory(transcribed_folder)
            
            if not os.path.isdir(mp3_folder):
                logging.warning(f"No 'mp3' folder in category: {category_path}")
                continue
            
            mp3_files = [f for f in os.listdir(mp3_folder) if f.lower().endswith('.mp3')]
            if not mp3_files:
                logging.info(f"No mp3 files found in: {mp3_folder}")
                continue
            
            print(f"\nTranscribing files in: {mp3_folder}")
            for mp3_file in tqdm(mp3_files, desc="Transcribing", unit="file"):
                mp3_path = os.path.join(mp3_folder, mp3_file)
                base_name = os.path.splitext(mp3_file)[0]
                transcript_path = os.path.join(transcribed_folder, base_name + ".txt")
                
                # Skip if transcript already exists
                if os.path.exists(transcript_path):
                    logging.info(f"Transcript already exists: {transcript_path}")
                    continue
                
                try:
                    # Transcribe mp3 directly
                    transcription = transcribe_audio(model, mp3_path, language=language)
                    
                    # Save transcription
                    if transcription:
                        with open(transcript_path, 'w', encoding='utf-8') as f:
                            f.write(transcription)
                        logging.info(f"Saved transcription: {transcript_path}")
                    else:
                        logging.warning(f"No transcription obtained for {mp3_path}.")
                    
                except Exception as e:
                    logging.error(f"Failed to process {mp3_path}: {e}")


def main():
    # Define the path to the parent directory
    parent_dir = os.getcwd() 

    # Choose the Whisper model size
    # Options: tiny, base, small, medium, large
    model_size = "large"  
    
    # Specify language for faster and more accurate transcription
    # If None, Whisper will auto-detect
    language = None  
    
    # Load the Whisper model
    model = load_whisper_model(model_size)
    
    # Start transcribing
    traverse_and_transcribe(parent_dir, model, language=language)
    
    print("\nTranscription process completed.")

if __name__ == "__main__":
    main()
