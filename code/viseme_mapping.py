import json

def map_phonemes_to_visemes(phoneme_data):
    """
    Map phoneme data to viseme data using the updated phoneme-to-image mappings.
    """
    phoneme_to_mouth_shape = {
        "AA": "aei.png", "AE": "aei.png", "AH": "aei.png", "AO": "o.png",
        "EH": "aei.png", "IH": "aei.png", "IY": "ee.png", "UH": "o.png", "UW": "o.png",
        "AY": "aei.png", "EY": "ee.png", "OW": "o.png", "OY": "o.png",
        "F": "fv.png", "V": "fv.png", "B": "bmp.png", "M": "bmp.png", "P": "bmp.png",
        "C": "cdgknstxyz.png", "D": "cdgknstxyz.png", "G": "cdgknstxyz.png",
        "K": "cdgknstxyz.png", "N": "cdgknstxyz.png", "S": "cdgknstxyz.png",
        "T": "cdgknstxyz.png", "X": "cdgknstxyz.png", "Y": "cdgknstxyz.png", "Z": "cdgknstxyz.png",
        "L": "l.png", "R": "r.png", "W": "qw.png", "Q": "qw.png",
        "SH": "shch.png", "CH": "shch.png", "JH": "shch.png",
        "TH": "th.png", "DH": "th.png", "SIL": "aei.png"
    }

    viseme_list = []
    for entry in phoneme_data:
        phoneme = entry['phoneme']
        mouth_shape = phoneme_to_mouth_shape.get(phoneme, "aei.png")  # Default to "aei.png"

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
