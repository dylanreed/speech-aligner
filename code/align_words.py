import os
from pocketsphinx import Pocketsphinx, get_model_path

def align_words(audio_file, transcript):
    model_path = get_model_path()
    config = {
        'verbose': True,
        'hmm': os.path.join(model_path, 'en-us', 'en-us'),
        'lm': os.path.join(model_path, '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/en-us-phone.lm.bin'),
        'dict': '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/cmudict-en-us.dict',
        'bestpath': True,  # Enable best path decoding
    }

    ps = Pocketsphinx(**config)
    ps.decode(audio_file=audio_file)

    hypothesis = ps.hypothesis()
    segments = ps.segments()

    print("Hypothesis:", hypothesis)
    print("Segments Debugging Output:", segments)

    word_data = []
    if segments:
        for segment in segments:
            # Check if segment contains timing information
            if hasattr(segment, 'word') and hasattr(segment, 'start_frame') and hasattr(segment, 'end_frame'):
                word_data.append({
                    'word': segment.word,
                    'start_time': segment.start_frame / 100.0,  # Convert frames to seconds
                    'end_time': segment.end_frame / 100.0,
                })
            else:
                print(f"Unexpected segment type: {segment}")

    return word_data

if __name__ == "__main__":
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Replace with your WAV file
    transcript = "What did one snowman say to the other snowman? Do you smell carrots?"  # Replace with your transcript
    aligned_words = align_words(audio_file, transcript)
    print("Aligned Words:")
    print(aligned_words)
