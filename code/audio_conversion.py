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
    input_audio = "/Users/nervous/Documents/GitHub/speech-aligner/inputs/nervous_2.mp3"
    output_wav = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"
    convert_to_wav(input_audio, output_wav)
