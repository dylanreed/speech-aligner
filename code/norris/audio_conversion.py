import os
import random
from pydub import AudioSegment

def add_analog_tape_effect(audio):
    """Simulate a subtle wow-and-flutter effect."""
    def apply_pitch_modulation(audio, rate):
        modulated = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * rate)})
        return modulated.set_frame_rate(audio.frame_rate)

    # Generate a subtle wobble in pitch
    wow_audio = apply_pitch_modulation(audio, 1.00001)  # Slight speed-up
    flutter_audio = apply_pitch_modulation(audio, 0.99998)  # Slight slow-down
    analog_audio = audio.overlay(wow_audio, gain_during_overlay=0).overlay(flutter_audio, gain_during_overlay=0)

    # Add subtle random volume fluctuations to simulate tape inconsistencies
    segments = []
    segment_duration = 25  # 25ms per segment for fine control
    for i in range(0, len(analog_audio), segment_duration):
        segment = analog_audio[i:i + segment_duration]
        fluctuation = random.uniform(-0.5, 0.5)  # Random fluctuation between -0.5 and +0.5 dB
        segments.append(segment.apply_gain(fluctuation))

    return sum(segments)

def convert_to_wav(input_file, output_file):
    """Convert an audio file to WAV format with modifications."""
    try:
        audio = AudioSegment.from_file(input_file)

        # Apply the analog tape effect
        audio = add_analog_tape_effect(audio)

        # Add 1 second of silence to the beginning and end
        silence = AudioSegment.silent(duration=1000)  # 1 second of silence
        audio = silence + audio + silence

        # Convert audio to desired properties
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # Export the audio to WAV format
        audio.export(output_file, format="wav")
        print(f"Converted and saved: {output_file}")
    except Exception as e:
        print(f"Error during conversion of {input_file}: {e}")

def main():
    # Input and output directories
    input_dir = "/Users/nervous/Documents/GitHub/speech-aligner/output/jokes_audio"
    output_dir = "/Users/nervous/Documents/GitHub/speech-aligner/output/converted_jokes"
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all audio files in the input directory
    for audio_file in os.listdir(input_dir):
        if audio_file.endswith(".mp3"):  # Process only .mp3 files
            input_file = os.path.join(input_dir, audio_file)
            output_file = os.path.join(output_dir, os.path.splitext(audio_file)[0] + ".wav")
            print(f"Processing {audio_file}...")
            convert_to_wav(input_file, output_file)

if __name__ == "__main__":
    main()
