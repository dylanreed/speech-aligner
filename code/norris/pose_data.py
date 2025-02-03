import re
import json
import os

def load_file(file_path):
    """
    Load text or JSON file content.
    Args:
        file_path (str): Path to the file.
    Returns:
        str or dict: File content (string for text files, dict for JSON files).
    """
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file format for file: {file_path}")

def parse_transcript_with_poses(transcript, words_timing):
    """
    Parse transcript for poses and generate timing data for each pose.

    Args:
        transcript (str): The transcript text with pose tags (e.g., "<wave>").
        words_timing (list): List of dictionaries with word timings, e.g.:
            [{"word": "Hello", "start_time": 0.0, "end_time": 0.5}, ...]

    Returns:
        list: Pose data with start and end times, e.g.:
            [{"pose": "wave", "start_time": 1.0, "end_time": 1.5}, ...]
    """
    # Pose tag regex
    pose_pattern = re.compile(r"<(.*?)>")
    
    # Match pose tags and associate them with word timings
    pose_data = []
    for match in re.finditer(pose_pattern, transcript):
        pose = match.group(1)  # Extract pose name
        # Approximate the position of the tag in the timeline
        position = match.start() / len(transcript) * words_timing[-1]["end_time"]
        # Find the closest word timing
        closest_word = min(
            words_timing,
            key=lambda x: abs(x["start_time"] - position)
        )
        pose_data.append({
            "pose_image": pose + ".png",
            "pose_start_time": closest_word["start_time"],
            "pose_end_time": closest_word["end_time"] + 0.5  # Extend duration by 0.5s
        })
    
    return pose_data

def save_pose_data(pose_data, output_file):
    """
    Save the pose data to a JSON file.
    Args:
        pose_data (list): Pose data to save.
        output_file (str): Path to the output JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(pose_data, f, indent=4)
    print(f"Pose data saved to: {output_file}")

if __name__ == "__main__":
    # File paths
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript_poses.txt"
    words_timing_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/word_data.json"
    output_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"

    # Load input files
    transcript = load_file(transcript_file)
    words_timing = load_file(words_timing_file)

    # Parse poses from the transcript
    pose_data = parse_transcript_with_poses(transcript, words_timing)

    # Save the pose data to a JSON file
    save_pose_data(pose_data, output_file)
