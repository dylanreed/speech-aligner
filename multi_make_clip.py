import os
import subprocess
import json

# Define paths
audio_dir = "/Users/nervous/Documents/GitHub/speech-aligner/output/converted_jokes"
output_dir = "/Users/nervous/Documents/GitHub/speech-aligner/output/finished_jokes"
script_dir = "/Users/nervous/Documents/GitHub/speech-aligner/code"

def run_script(script_name, *args):
    """Run a Python script with optional arguments."""
    script_path = os.path.join(script_dir, script_name)
    try:
        subprocess.run(["python", script_path, *args], check=True)
        print(f"Successfully ran {script_name} with arguments: {args}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

def process_audio_file(audio_file, output_base):
    """Process an individual audio file."""
    print(f"Processing {audio_file}...")

    # 1. Transcribe audio
    transcript_file = f"{output_base}_transcript.txt"
    run_script("transcript-from-wav.py", audio_file, transcript_file)

    # 2. Align words
    word_data_file = f"{output_base}_word_data.json"
    run_script("create-word-data.py", audio_file, transcript_file, word_data_file)

    # 3. Map phonemes
    phoneme_data_file = f"{output_base}_phoneme_data.json"
    run_script("phoneme_mapping.py", word_data_file, phoneme_data_file)

    # 4. Map visemes
    viseme_data_file = f"{output_base}_viseme_data.json"
    run_script("viseme_mapping.py", phoneme_data_file, viseme_data_file)

    # 5. Animate poses and generate video
    temp_dir = os.path.join(output_dir, "tmp_frames")
    output_video = f"{output_base}_video.mp4"
    final_video = f"{output_base}_final_video.mp4"
    run_script("animate_poses.py", viseme_data_file, audio_file, temp_dir, output_video, final_video)

    print(f"Finished processing {audio_file}. Final video saved to {final_video}")

def main():
    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each audio file in the converted directory
    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav"):
            audio_path = os.path.join(audio_dir, audio_file)
            output_base = os.path.join(output_dir, os.path.splitext(audio_file)[0])
            process_audio_file(audio_path, output_base)

if __name__ == "__main__":
    main()
