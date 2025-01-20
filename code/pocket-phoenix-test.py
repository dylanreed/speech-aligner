from pocketsphinx import Pocketsphinx, get_model_path
import os

model_path = get_model_path()
config = {
    'hmm': os.path.join(model_path, 'en-us', 'en-us'),
    'lm': os.path.join(model_path, '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/en-us.lm.bin'),
    'dict': '/Users/nervous/Documents/GitHub/speech-aligner/.venv/lib/python3.10/site-packages/pocketsphinx/model/en-us/cmudict-en-us.dict',
}

try:
    ps = Pocketsphinx(**config)
    print("PocketSphinx initialized successfully!")
except Exception as e:
    print(f"Initialization failed: {e}")