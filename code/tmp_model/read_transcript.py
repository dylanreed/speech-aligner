def read_transcript(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Transcript file not found at {file_path}")
        return None

if __name__ == "__main__":
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript.txt"
    transcript = read_transcript(transcript_file)
    if transcript:
        print("Transcript loaded:")
        print(transcript)