import json

pose_data = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"

pose_data_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"

with open(pose_data, "r", encoding="utf-8") as f:
    pose_data = json.load(f)

print("Loaded pose_data:", pose_data)

for entry in pose_data:
    if not isinstance(entry, dict):
        raise ValueError(f"Invalid entry in pose_data: {entry}")
    required_keys = ["pose_start_time", "pose_end_time", "pose_image"]
    for key in required_keys:
        if key not in entry:
            raise ValueError(f"Missing key '{key}' in entry: {entry}")

