import json
from phonemizer import phonemize  # Install with `pip install phonemizer`
from pydub import AudioSegment  # Install with `pip install pydub`

def load_phoneme_viseme_map():
    """Defines a mapping of phonemes to visemes (mouth shapes)."""
    return {
        "a": "mouth_open",
        "e": "smile",
        "i": "narrow_smile",
        "o": "round_open",
        "u": "pucker",
        "m": "closed",
        "p": "p_outward",
        "f": "teeth_upper",
        "s": "teeth_open",
        "t": "flat_open",
        # Add other phoneme mappings
    }

def read_transcript(file_path):
    """Reads the transcript text from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

def get_audio_duration(audio_file):
    """Gets the duration of the audio file in milliseconds."""
    audio = AudioSegment.from_file(audio_file)
    return len(audio)

def map_phonemes_to_visemes_with_timing(transcript, audio_duration):
    """Converts transcript into a list of visemes with timing."""
    phoneme_viseme_map = load_phoneme_viseme_map()

    # Phonemize the transcript
    phonemes = phonemize(transcript, language="en-us", backend="espeak", strip=True)

    # Placeholder: Evenly distribute phonemes over the audio duration
    viseme_list = []
    phoneme_count = len(phonemes)
    time_per_phoneme = audio_duration / phoneme_count if phoneme_count else 0

    current_time = 0
    for phoneme in phonemes:
        viseme = phoneme_viseme_map.get(phoneme, "neutral")  # Default to 'neutral'
        viseme_list.append({
            "viseme": viseme,
            "start_time": current_time,
            "end_time": current_time + time_per_phoneme
        })
        current_time += time_per_phoneme

    return viseme_list

# Example usage
if __name__ == "__main__":
    # File paths
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript.txt"
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"

    # Read transcript from the file
    transcript = read_transcript(transcript_file)

    if transcript:
        # Get audio duration
        audio_duration = get_audio_duration(audio_file)

        # Process the transcript to assign visemes with timing
        visemes = map_phonemes_to_visemes_with_timing(transcript, audio_duration)

        # Output viseme sequence with timing
        json_object = json.dumps(visemes, indent=4)
        with open("/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_squence.json", "w") as outfile:
            outfile.write(json_object)
        #print(json.dumps(visemes, indent=2))
