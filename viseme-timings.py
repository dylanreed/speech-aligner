import os
import json
from pocketsphinx import AudioFile, get_model_path
from pydub import AudioSegment

def convert_to_wav(input_file, output_file):
    """
    Convert an audio file to WAV format (16 kHz, mono).

    :param input_file: Path to the input audio file.
    :param output_file: Path to save the converted WAV file.
    """
    try:
        audio = AudioSegment.from_file(input_file)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_file, format="wav")
        print(f"File converted to WAV successfully: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")


def read_transcript(file_path):
    """
    Read the transcript text from a file.

    :param file_path: Path to the transcript file.
    :return: Transcript text.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Transcript file not found at {file_path}")
        return None

def align_words(audio_file, transcript):
    """
    Align words in the audio file with the transcript using PocketSphinx.

    :param audio_file: Path to the WAV file.
    :param transcript: Transcript of the audio.
    :return: List of words with their start and end times.
    """
    model_path = get_model_path()

    config = {
        'verbose': False,
        'audio_file': audio_file,
        'hmm': os.path.join(model_path, 'en-us', 'en-us'),
        'lm': os.path.join(model_path, '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/en-us.lm.bin'),
        'dict': '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/cmudict-en-us.dict',
    }

    word_data = []
    audio = AudioFile(**config)

    for segment in audio:
        if hasattr(segment, 'word') and segment.word not in ('<s>', '</s>'):
            word_data.append({
                'word': segment.word,
                'start_time': segment.start_frame / 100.0,  # Convert frames to seconds
                'end_time': segment.end_frame / 100.0
            })

    return word_data

def map_words_to_phonemes(word_data):
    """
    Map words to phonemes using a phoneme dictionary and provide timings.

    :param word_data: List of words with start and end timings.
    :return: List of phonemes with start and end timings.
    """
    # Load CMU Pronouncing Dictionary
    cmu_dict = {
        "example": ["EH1", "G", "Z", "AE1", "M", "P", "L"],  # Add more mappings here
        # Extend with a proper CMU dictionary for real use
    }

    phoneme_data = []
    for word_entry in word_data:
        word = word_entry['word'].lower()
        start_time = word_entry['start_time']
        end_time = word_entry['end_time']
        word_duration = end_time - start_time

        # Get phonemes for the word
        phonemes = cmu_dict.get(word, ["SIL"])  # Default to 'SIL' for silence

        # Evenly distribute phonemes over word duration
        num_phonemes = len(phonemes)
        phoneme_duration = word_duration / num_phonemes if num_phonemes else 0

        current_time = start_time
        for phoneme in phonemes:
            phoneme_data.append({
                'phoneme': phoneme,
                'start_time': current_time,
                'end_time': current_time + phoneme_duration
            })
            current_time += phoneme_duration

    return phoneme_data

def map_phonemes_to_visemes(phoneme_data):
    """
    Map phonemes to visemes using a predefined dictionary.

    :param phoneme_data: List of phonemes with timing information.
    :return: List of visemes with timing information.
    """
    phoneme_viseme_map = {
"AA": "wide_open",
        "AE": "mouth_open",
        "AH": "neutral",
        "AO": "round_open",
        "AW": "pucker_open",
        "AY": "smile_open",
        "B": "closed",
        "CH": "teeth_open",
        "D": "neutral",
        "DH": "teeth_slight_open",
        "EH": "mouth_mid_open",
        "ER": "tight_lips",
        "EY": "smile_closed",
        "F": "teeth_upper",
        "G": "closed",
        "HH": "wide_breath",
        "IH": "small_open",
        "IY": "smile_open",
        "JH": "slight_teeth",
        "K": "closed",
        "L": "neutral",
        "M": "closed",
        "N": "neutral",
        "NG": "neutral",
        "OW": "round_closed",
        "OY": "pucker_smile",
        "P": "p_outward",
        "R": "tight_lips",
        "S": "teeth_open",
        "SH": "teeth_slit",
        "T": "flat_open",
        "TH": "tongue_between",
        "UH": "pucker",
        "UW": "tight_pucker",
        "V": "teeth_upper",
        "W": "pucker_wide",
        "Y": "smile_narrow",
        "Z": "teeth_open",
        "ZH": "teeth_slit",
        "SIL": "neutral",        
    }

    viseme_list = []
    for entry in phoneme_data:
        viseme = phoneme_viseme_map.get(entry['phoneme'], "neutral")  # Default to 'neutral'
        viseme_list.append({
            "viseme": viseme,
            "start_time": entry['start_time'],
            "end_time": entry['end_time']
        })

    return viseme_list

if __name__ == "__main__":
    # File paths
    input_audio = "/Users/nervous/Documents/GitHub/speech-aligner/inputs/audio.m4a"  # Replace with your audio file
    output_wav = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Path for WAV file
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript.txt"  # Path to transcript file
    viseme_output_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_sequence.json"  # Output JSON file for viseme sequence

    # Step 1: Convert audio to WAV
    convert_to_wav(input_audio, output_wav)

    # Step 2: Read transcript
    transcript = read_transcript(transcript_file)

    if transcript:
        # Step 3: Align words
        word_data = align_words(output_wav, transcript)

        # Step 4: Map words to phonemes
        phoneme_data = map_words_to_phonemes(word_data)

        # Step 5: Map phonemes to visemes
        viseme_data = map_phonemes_to_visemes(phoneme_data)

        # Step 6: Save viseme sequence to JSON
        try:
            with open(viseme_output_file, "w") as outfile:
                json.dump(viseme_data, outfile, indent=4)
            print(f"Viseme sequence saved to {viseme_output_file}")
        except Exception as e:
            print(f"Error saving viseme sequence: {e}")
