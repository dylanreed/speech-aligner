import pandas as pd
import requests
import os

# Function to interact with Eleven Labs API and create audio
def text_to_speech(api_key, voice_id, text, output_file):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",  # Adjust model if needed
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Audio saved to {output_file}")
    else:
        print(f"Failed to generate audio: {response.status_code}, {response.text}")

# Main script
def main():
    # Path to your CSV file
    csv_file = "/Users/nervous/Documents/GitHub/speech-aligner/inputs/jokes/jokes_test.csv"
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Assume the CSV has a column named 'text' with the lines
    lines = df['text'].tolist()

    # Eleven Labs API settings
    api_key = "sk_176192a20220752b5863e294703ea73200898bf126ebb3e2"  # Replace with your API key
    voice_id = "i1CsF0dbxtrr78piuktK"           # Replace with the desired voice ID

    # Iterate through lines in the CSV and generate audio for each
    output_dir = "/Users/nervous/Documents/GitHub/speech-aligner/output/jokes_audio/output.wav"
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, line in enumerate(lines):
        output_file = os.path.join(output_dir, f"joke_{idx + 1}.mp3")
        print(f"Generating audio for line {idx + 1}: {line}")
        text_to_speech(api_key, voice_id, line, output_file)

if __name__ == "__main__":
    main()
