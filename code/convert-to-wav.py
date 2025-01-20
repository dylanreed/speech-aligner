from pydub import AudioSegment

def convert_to_wav(input_file, output_file):
    """
    Convert an audio file to WAV format.
    
    :param input_file: Path to the input audio file.
    :param output_file: Path to save the converted WAV file.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        
        # Export as WAV
        audio.export(output_file, format="wav")
        print(f"File converted successfully: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

# Example usage
input_audio = "/Users/nervous/Documents/GitHub/speech-aligner/inputs/audio.m4a"  # Replace with your input file
output_audio = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Replace with desired output file

convert_to_wav(input_audio, output_audio)