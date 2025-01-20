def load_cmu_dict(file_path):
    cmu_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith(";;;"):
                    parts = line.strip().split("  ")
                    if len(parts) == 2:
                        word, phonemes = parts
                        cmu_dict[word.lower()] = phonemes.split()
    except Exception as e:
        print(f"Error loading CMU dictionary: {e}")
    return cmu_dict

def map_words_to_phonemes(word_data, cmu_dict):
    phoneme_data = []
    for word_entry in word_data:
        word = word_entry['word'].lower().strip("()[]0123456789")
        start_time = word_entry['start_time']
        end_time = word_entry['end_time']
        word_duration = end_time - start_time

        phonemes = cmu_dict.get(word, ['SIL'])
        phoneme_duration = word_duration / len(phonemes) if phonemes else 0

        current_time = start_time
        for phoneme in phonemes:
            phoneme_data.append({
                'phoneme': phoneme,
                'start_time': current_time,
                'end_time': current_time + phoneme_duration
            })
            current_time += phoneme_duration

    return phoneme_data

if __name__ == "__main__":
    word_data = [{"word": "hello", "start_time": 0.0, "end_time": 1.0}]
    cmu_dict_path = "path/to/cmudict-en-us.dict"
    cmu_dict = load_cmu_dict(cmu_dict_path)
    phoneme_data = map_words_to_phonemes(word_data, cmu_dict)
    print("Phoneme Data:")
    print(phoneme_data)
