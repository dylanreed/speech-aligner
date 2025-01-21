
from tqdm import tqdm
import pygame
import json
import os
import subprocess

def load_viseme_data(viseme_file):
    """Load viseme data from a JSON file."""
    with open(viseme_file, "r", encoding="utf-8") as f:
        return json.load(f)

def render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir):
    """Render animation frames and encode them into a video, with neutral frames during silence."""
    # Initialize Pygame
    pygame.init()

    # Set up display (off-screen rendering)
    screen = pygame.Surface(resolution)

    # Load images
    # Load head image
    if os.path.exists(head_image_path):
        head_image = pygame.image.load(head_image_path)
    else:
        raise FileNotFoundError(f"Head image not found: {head_image_path}")
    #load mouth shapes
    images = {}
    for entry in viseme_data:
        mouth_shape = entry["mouth_shape"]
        if mouth_shape not in images:
            image_path = os.path.join(image_directory, mouth_shape)
            if os.path.exists(image_path):
                images[mouth_shape] = pygame.image.load(image_path)

    # Ensure the neutral frame is loaded
    neutral_image_path = os.path.join(image_directory, "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes/positive/smile.png")
    if os.path.exists(neutral_image_path):
        images["neutral"] = pygame.image.load(neutral_image_path)
    else:
        raise FileNotFoundError("Neutral frame ('smile.png') not found in the image directory.")

    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Render frames
    total_frames = int(viseme_data[-1]["end_time"] * fps)
    frame_time = 1 / fps
    current_time = 0.0

    print(f"Rendering {total_frames} frames...")
    for frame_number in tqdm(range(total_frames), desc="Rendering Frames"):
        # Clear screen
        screen.fill((211, 211, 211))  # Light grey background color

     # Draw the head image centered on the screen
        head_x = resolution[0] // 2 - head_image.get_width() // 2
        head_y = resolution[1] // 2 - head_image.get_height() // 2
        screen.blit(head_image, (head_x, head_y))

        # Determine which viseme to show
        displayed_image = "neutral"
        for entry in viseme_data:
            viseme_start = entry["start_time"]
            viseme_end = entry["end_time"]
            mouth_shape = entry["mouth_shape"]

            if viseme_start <= current_time < viseme_end:
                displayed_image = mouth_shape
                break

        # Display the selected image (neutral if no viseme active)
        if displayed_image in images:
            mouth_image = images[displayed_image]
            mouth_x = head_x + head_image.get_width() // 2 - mouth_image.get_width() // 2
            mouth_y = head_y + head_image.get_height() // 2 - mouth_image.get_height() // 2
            screen.blit(mouth_image, (mouth_x, mouth_y))


        # Save the frame as an image
        frame_path = os.path.join(temp_dir, f"frame_{frame_number:04d}.png")
        pygame.image.save(screen, frame_path)

        # Increment time
        current_time += frame_time

    # Encode frames to video
    print("Encoding video...")
    ffmpeg_command = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_video
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"Video saved to {output_video}")

def combine_audio_with_video(video_file, audio_file, output_file):
    """Combine the rendered video and audio into a single file."""
    print("Adding audio to video...")
    ffmpeg_command = [
        "ffmpeg", "-y", "-i", video_file, "-i", audio_file, 
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_file
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"Final video with audio saved to {output_file}")

if __name__ == "__main__":
    # Paths
    viseme_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_data.json"  # Replace with your viseme data file
    image_directory = "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes/positive/"  # Directory containing mouth shape images
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Path to the audio file
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/tmp_frames/"  # Directory to store temporary frames
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_video.mp4"  # Video without audio
    final_output = "/Users/nervous/Documents/GitHub/speech-aligner/output/final_output_with_audio.mp4"  # Final video with audio
    head_image_path ="/Users/nervous/Documents/GitHub/speech-aligner/assets/the dude.png"
    # Configuration
    fps = 30  # Frames per second
    resolution = (800, 600)  # Video resolution

    # Load viseme data
    viseme_data = load_viseme_data(viseme_file)

    # Render animation to video
    render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir)

    # Combine video with audio
    combine_audio_with_video(output_video, audio_file, final_output)
