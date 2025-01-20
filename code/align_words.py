import os
from pocketsphinx import Pocketsphinx, get_model_path

def align_words(audio_file, transcript):
    model_path = get_model_path()
    config = {
        'verbose': True,
        'hmm': os.path.join(model_path, 'en-us', 'en-us'),
        'lm': os.path.join(model_path, '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/en-us.lm.bin'),
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
    transcript = "Writing is hard. I think we can all agree that writing is hard. When I say it is hard, I mean that consistently writing is hard. I love writing, I just wish I did it more. I recently stumbled upon my collection of notebooks from when I was writing my first full novel. Reading through them showed me that I have a lot of fun ideas. I just need to get them out of my head and onto some pages. I'm currently trying to transfer all the notebooks into my remarkable two, tablet. I'm sure I could scan them in and save them as PDFs, but it has been a lot of fun reading and copying over the notes. The only problem is that I don't write by hand very much anymore, so my hand is getting so tired. It also doesn't help that my remarkable marker pro broke so it doesn't work great anymore. I have a new pin thing coming so I can continue to transfer to the remarkable and then I need to rewrite the first novel with all of the new knowledge and time."  # Replace with your transcript
    aligned_words = align_words(audio_file, transcript)
    print("Aligned Words:")
    print(aligned_words)
