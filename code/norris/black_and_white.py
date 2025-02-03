import subprocess

def add_grain_to_video(input_video, output_video):
    """
    Adds grain to a video using FFmpeg and saves the output.
    
    Args:
        input_video (str): Path to the input video.
        output_video (str): Path to save the output video with grain effect.
    """
    ffmpeg_command = [
        "ffmpeg", "-y",  # Overwrite output file if it exists
        "-i", input_video,  # Input video
        "-vf", "hue=s=0,boxblur=lr=1.2,noise=c0s=7:allf=t,format=yuv420p",  # Filters
        "-c:v", "libx264",  # Video codec
        "-c:a", "copy",  # Copy audio without re-encoding
        output_video  # Output video path
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Grainy video saved to {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error applying grain effect: {e}")

# Example usage
input_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/with_audio.mp4"
output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/black_and_white.mp4"

add_grain_to_video(input_video, output_video)
