import whisper

def transcribe_and_save(audio_file, model_name="base", transcript_file="transcript.txt"):
    """
    Transcribe an audio file using Whisper and save the transcription as a text file.

    :param audio_file: Path to the audio file to transcribe.
    :param model_name: Whisper model to use (e.g., "base", "small", "medium", "large").
    :param transcript_file: Path to save the transcription as a text file.
    """
    # Load Whisper model
    model = whisper.load_model(model_name)

    # Transcribe audio
    print("Transcribing audio...")
    result = model.transcribe(audio_file)

    # Extract transcription text
    transcription = result.get("text", "").strip()

    # Save transcription to a text file
    try:
        with open(transcript_file, "w") as f:
            f.write(transcription)
        print(f"Transcription saved to {transcript_file}")
    except Exception as e:
        print(f"Error saving transcription:{e}")

# Example usage
audio_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Path to your audio file
output_text_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript.txt"  # Path to save the transcription
transcribe_and_save(audio_path, transcript_file=output_text_file)
