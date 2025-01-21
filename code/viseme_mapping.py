import json

def map_phonemes_to_visemes(phoneme_data):
    """
    Map phoneme data to viseme data using descriptive-to-image file mappings.
    """
    # Descriptive viseme to image file mapping
    viseme_to_image_map = {
        "wide_open": "1.png",
        "mouth_open": "2.png",
        "neutral": "neutral.png",
        "teeth_showing": "8.png",
        "tongue_out": "7.png",
        "lips_tight": "11.png",
        "teeth_close": "7.png",
        "puckered": "11.png",
        "tongue_top": "8.png",
    }

    # Phoneme-to-descriptive-viseme mapping
    phoneme_viseme_map = {
        "AA": "wide_open", "AE": "mouth_open", "AH": "neutral",
        "SIL": "neutral", "F": "teeth_showing", "V": "teeth_showing",
        "TH": "tongue_out", "DH": "tongue_out", "S": "teeth_close",
        "Z": "teeth_close", "SH": "lips_tight", "CH": "lips_tight",
        "T": "tongue_top", "D": "tongue_top", "N": "tongue_top",
        # Add other phonemes as needed
    }

    viseme_list = []
    for entry in phoneme_data:
        phoneme = entry['phoneme']

        # Map phoneme to descriptive viseme
        descriptive_viseme = phoneme_viseme_map.get(phoneme, "neutral")
        
        # Map descriptive viseme to image file
        mouth_shape = viseme_to_image_map.get(descriptive_viseme, "neutral.png")

        # Debugging: Print the mapping process
        print(f"Phoneme: {phoneme}, Descriptive Viseme: {descriptive_viseme}, Mouth Shape: {mouth_shape}")

        # Add to viseme list
        viseme_list.append({
            "mouth_shape": mouth_shape,
            "start_time": entry['start_time'],
            "end_time": entry['end_time']
        })

    return viseme_list

if __name__ == "__main__":
    # Load phoneme data from the JSON file
    phoneme_data_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/phoneme_data.json"  # Replace with the actual file path
    with open(phoneme_data_path, "r", encoding="utf-8") as json_file:
        phoneme_data = json.load(json_file)

    # Map phonemes to visemes
    viseme_data = map_phonemes_to_visemes(phoneme_data)

    # Save viseme data to a new JSON file
    viseme_data_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_data.json"
    with open(viseme_data_path, "w", encoding="utf-8") as json_file:
        json.dump(viseme_data, json_file, indent=4)

    print(f"Viseme data has been exported to {viseme_data_path}")
