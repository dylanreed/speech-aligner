def map_phonemes_to_visemes(phoneme_data):
    phoneme_viseme_map = {
        "AA": "wide_open", "AE": "mouth_open", "AH": "neutral",  # Add other mappings...
        "SIL": "neutral",
    }

    viseme_list = []
    for entry in phoneme_data:
        viseme = phoneme_viseme_map.get(entry['phoneme'], "neutral")
        viseme_list.append({
            "viseme": viseme,
            "start_time": entry['start_time'],
            "end_time": entry['end_time']
        })

    return viseme_list

if __name__ == "__main__":
    phoneme_data = [{"phoneme": "AH", "start_time": 0.0, "end_time": 0.5}]
    viseme_data = map_phonemes_to_visemes(phoneme_data)
    print("Viseme Data:")
    print(viseme_data)
