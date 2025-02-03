from pyAudioAnalysis import audioSegmentation as aS
import os

def extract_emotions_with_pyaudioanalysis(audio_path, model_path, model_type="svm"):
    """
    Extract emotions and their timings from an audio file using pyAudioAnalysis.

    Args:
        audio_path (str): Path to the audio file.
        model_path (str): Path to the pretrained model.
        model_type (str): Type of the model (e.g., "svm", "knn").

    Returns:
        list of tuples: Each tuple contains (start_time, end_time, emotion_label).
    """
    # Ensure the audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    try:
        # Perform mid-term segmentation and classification
        segments, classes = aS.mid_term_file_classification(
            audio_path,
            model_path,
            model_type
        )

        # Prepare results
        results = []
        for i, segment in enumerate(segments):
            start_time = segment[0]
            end_time = segment[1]
            emotion_label = classes[i]
            results.append((start_time, end_time, emotion_label))

        return results

    except Exception as e:
        print(f"Error during emotion extraction: {e}")
        return []


# Example usage
if __name__ == "__main__":
    # Path to the audio file
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"

    # Path to the pretrained model (replace with your actual model path)
    model_path = "path_to_pretrained_model"  # e.g., svmModel

    try:
        # Extract emotions and timings
        emotions = extract_emotions_with_pyaudioanalysis(audio_file, model_path, model_type="svm")

        # Print results
        for start_time, end_time, emotion in emotions:
            print(f"From {start_time:.2f}s to {end_time:.2f}s: {emotion}")

    except FileNotFoundError as fnf_error:
        print(fnf_error)
