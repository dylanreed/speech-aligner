import sys
import os
from pydub import AudioSegment

def convert_to_wav(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_file, format="wav")
        print(f"File converted to WAV successfully: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

def main():
    # Prompt user for the audio file name
    audio_file_name = input("Please enter the name of your audio file (with extension): ").strip()
    audio_file_path = os.path.join("/Users/nervous/Documents/GitHub/speech-aligner/inputs", audio_file_name)
    output_wav_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"

    if not os.path.exists(audio_file_path):
        print(f"Error: The file {audio_file_path} does not exist. Please check the file name and try again.")
        exit(1)

    print(f"Using audio file: {audio_file_path}")



    # Perform the conversion
    convert_to_wav(audio_file_path, output_wav_path)

if __name__ == "__main__":
    main()
