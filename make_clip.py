import subprocess
import os
import shutil

def duplicate_transcript(original_path, duplicate_path):
    """Duplicate the transcript file."""
    try:
        shutil.copy(original_path, duplicate_path)
        print(f"Duplicated {original_path} to {duplicate_path}.")
    except FileNotFoundError:
        print(f"Error: {original_path} does not exist. Ensure the file is in the correct location.")
        exit(1)

def pause_for_edit(file_path):
    """Pause execution to allow editing of a file."""
    print(f"\nPlease edit the file: {file_path}.")
    print("Press Enter when you are done editing and ready to continue.Availible poses are <fist> <wave> <point>")
    input()  # Wait for the user to press Enter

def run_script(script_path, *args):
    """Run a Python script using subprocess with optional arguments."""
    try:
        subprocess.run(["python", script_path, *args], check=True)
        print(f"Successfully ran: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_path}: {e}")

def main():
    # Prompt user for the audio file name
    audio_file_name = input("Please enter the name of your audio file (with extension): ").strip()
    audio_file_path = os.path.join("/Users/nervous/Documents/GitHub/speech-aligner/inputs", audio_file_name)
    output_wav_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"

    if not os.path.exists(audio_file_path):
        print(f"Error: The file {audio_file_path} does not exist. Please check the file name and try again.")
        exit(1)

    print(f"Using audio file: {audio_file_path}")

    script_dir = "/Users/nervous/Documents/GitHub/speech-aligner/code"
    audio_conversion_script = os.path.join(script_dir, "/Users/nervous/Documents/GitHub/speech-aligner/code/audio_conversion.py")

    # Run audio_conversion.py with input and output arguments
    run_script(audio_conversion_script, audio_file_path, output_wav_path)


def main():
    """Main function to execute scripts in sequence."""
    # Prompt user for the audio file name
    audio_file_name = input("Please enter the name of your audio file (with extension): ").strip()

    # Validate the file exists
    audio_file_path = os.path.join("/Users/nervous/Documents/GitHub/speech-aligner/inputs", audio_file_name)
    if not os.path.exists(audio_file_path):
        print(f"Error: The file {audio_file_path} does not exist. Please check the file name and try again.")
        exit(1)

    print(f"Using audio file: {audio_file_path}")

    script_dir = "/Users/nervous/Documents/GitHub/speech-aligner/code"  # Path to the folder containing the scripts
    scripts = [
        "audio_conversion.py",
        "transcript-from-wav.py",  # Run this first
    ]
    remaining_scripts = [
        "create-word-data.py",
        "phoneme_mapping.py",
        "viseme_mapping.py",
        "pose_data.py",
        "animate_poses.py"
    ]

    # Run the first set of scripts
    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if os.path.exists(script_path):
            run_script(script_path)
        else:
            print(f"Script not found: {script_path}")

    # Step 1: Duplicate transcript.txt to transcript_poses.txt
    transcript_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript.txt"
    transcript_poses_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript_poses.txt"
    duplicate_transcript(transcript_path, transcript_poses_path)

    # Step 2: Pause to allow editing of transcript_poses.txt
    pause_for_edit(transcript_poses_path)

    # Step 3: Run the remaining scripts
    for script in remaining_scripts:
        script_path = os.path.join(script_dir, script)
        if os.path.exists(script_path):
            run_script(script_path)
        else:
            print(f"Script not found: {script_path}")

if __name__ == "__main__":
    main()
