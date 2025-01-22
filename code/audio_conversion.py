import sys
from pydub import AudioSegment

def convert_to_wav(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_file, format="wav")
        print(f"File converted to WAV successfully: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python audio_conversion.py <input_file> <output_file>")
        sys.exit(1)

    input_audio = sys.argv[1]
    output_wav = sys.argv[2]
    convert_to_wav(input_audio, output_wav)
    print(f"sys.argv[2] (output file): {sys.argv[2]}")