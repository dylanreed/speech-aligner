import whisper
import json

model = whisper.load_model("medium")
result = model.transcribe("/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav", word_timestamps=True)

# Print the entire result to understand its structure
print(result)

word_data = []
for segment in result['segments']:
    for word in segment['words']:
        word_data.append({
            "word": word["word"],  # Use "word" key instead of "text"
            "start_time": word["start"],
            "end_time": word["end"]
        })

# Export word data to a JSON file
output_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/word_data.json"
with open(output_path, "w", encoding="utf-8") as json_file:
    json.dump(word_data, json_file, indent=4, ensure_ascii=False)

