import sys
import os
import random
from pydub import AudioSegment
from pydub.generators import Sine

def add_analog_tape_effect(audio):
    # Simulate a subtle wow-and-flutter effect
    def apply_pitch_modulation(audio, rate):
        modulated = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * rate)})
        return modulated.set_frame_rate(audio.frame_rate)

    # Generate a subtle wobble in pitch
    wow_audio = apply_pitch_modulation(audio, 1.00000000001)  # Slight speed-up
    flutter_audio = apply_pitch_modulation(audio, .99999999999998)  # Slight slow-down
    analog_audio = audio.overlay(wow_audio, gain_during_overlay=0).overlay(flutter_audio, gain_during_overlay=0)

    # Add subtle random volume fluctuations to simulate tape inconsistencies
    segments = []
    segment_duration = 25  # 50ms per segment for fine control
    for i in range(0, len(analog_audio), segment_duration):
        segment = analog_audio[i:i + segment_duration]
        fluctuation = random.uniform(-.5, .5)  # Random fluctuation between -1.5 and +1.5 dB
        segments.append(segment.apply_gain(fluctuation))

    return sum(segments)

def convert_to_wav(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)



        # Apply the analog tape effect
        audio = add_analog_tape_effect(audio)

         # Add 2 seconds of silence to the beginning and end of the audio
        silence = AudioSegment.silent(duration=1500)  # 2 seconds of silence
        audio = silence + audio + silence

        # Convert audio to desired properties
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # Export the audio to WAV format
        audio.export(output_file, format="wav")
        print(f"File converted to WAV successfully with analog tape effect: {output_file}")
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
