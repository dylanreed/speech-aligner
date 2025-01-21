import json

def load_cmu_dict(file_path):
    """Load the CMU Pronouncing Dictionary."""
    cmu_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith(";;;"):  # Skip comment lines
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        word, phonemes = parts
                        cmu_dict[word] = phonemes.split()
    except Exception as e:
        print(f"Error loading CMU dictionary: {e}")
    print(f"Loaded {len(cmu_dict)} entries from the CMU dictionary.")
    return cmu_dict

def map_words_to_phonemes(word_data, cmu_dict):
    phoneme_data = []
    unmatched_words = []

    for word_entry in word_data:
        # Normalize the word
        word = word_entry['word'].lower().strip("()[]0123456789.,!?\"' ").strip()
        start_time = word_entry['start_time']
        end_time = word_entry['end_time']
        word_duration = end_time - start_time

        # Try exact match or variant match
        phonemes = cmu_dict.get(word) or next(
            (v for k, v in cmu_dict.items() if k.startswith(word + "(")), ['SIL']
        )

        # Log if the word is not found
        if phonemes == ['SIL']:
            unmatched_words.append(word)
            print(f"Word '{word}' not found in CMU dictionary. Using fallback 'SIL'.")
        else:
            print(f"Word '{word}' mapped to phonemes: {phonemes}")

        # Distribute duration across phonemes
        phoneme_duration = word_duration / len(phonemes) if phonemes else 0
        current_time = start_time

        for phoneme in phonemes:
            phoneme_data.append({
                'phoneme': phoneme,
                'start_time': current_time,
                'end_time': current_time + phoneme_duration
            })
            current_time += phoneme_duration

    # Print unmatched words for debugging
    if unmatched_words:
        print("Unmatched words:", unmatched_words)

    return phoneme_data


def main():
    # Path to CMU dictionary
    cmu_dict_path = "/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/cmudict-en-us.dict"  # Replace with your actual path
    cmu_dict = load_cmu_dict(cmu_dict_path)

    # Load the word data JSON
    word_data_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/word_data.json"  # Replace with your word data JSON file path
    with open(word_data_path, "r", encoding="utf-8") as json_file:
        word_data = json.load(json_file)

    # Map words to phonemes
    phoneme_data = map_words_to_phonemes(word_data, cmu_dict)

    # Save the phoneme data to JSON
    output_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/phoneme_data.json"
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(phoneme_data, json_file, indent=4, ensure_ascii=False)

    print(f"Phoneme data has been exported to {output_path}")

if __name__ == "__main__":
    main()
