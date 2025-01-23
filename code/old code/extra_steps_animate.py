
from tqdm import tqdm
import pygame
import json
import os
import subprocess
import random

def load_viseme_data(viseme_file):
    """Load viseme data from a JSON file."""
    with open(viseme_file, "r", encoding="utf-8") as f:
        return json.load(f)
    

def render_animation_to_video(
    viseme_data, mouth_image_path, output_video, fps, resolution, temp_dir, 
    head_image_path, blink_image_path, pose_image_path, pose_data_path
):
    """
    Renders an animation in three stages:
    1. Adds mouth shapes and saves the video.
    2. Adds blinking and saves the video.
    3. Adds poses and saves the final video.
    """
    # Initialize Pygame
    pygame.init()

    # Set up the display surface (off-screen rendering)
    screen = pygame.Surface(resolution)

    # Load images
    if not os.path.exists(head_image_path):
        raise FileNotFoundError(f"Head image not found: {head_image_path}")
    head_image = pygame.image.load(head_image_path)

    if not os.path.exists(blink_image_path):
        raise FileNotFoundError(f"Blink image not found: {blink_image_path}")
    blink_image = pygame.image.load(blink_image_path)

    viseme_images = {
        file_name.replace(".png", ""): pygame.image.load(os.path.join(mouth_image_path, file_name))
        for file_name in os.listdir(mouth_image_path) if file_name.endswith(".png")
    }

    with open(pose_data_path, "r", encoding="utf-8") as f:
        pose_data = json.load(f)

    if not isinstance(pose_data, list):
        raise TypeError(f"pose_data should be a list, got {type(pose_data)}")

    pose_images = {
        file_name.replace(".png", ""): pygame.image.load(os.path.join(pose_image_path, file_name))
        for file_name in os.listdir(pose_image_path) if file_name.endswith(".png")
    }
    if "neutral" not in pose_images:
        raise FileNotFoundError("Neutral pose image not found")

    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Stage 1: Render mouth shapes
    mouth_video_path = os.path.join(temp_dir, "mouth_shapes.mp4")
    render_stage(screen, resolution, viseme_data, fps, head_image, viseme_images, None, None, mouth_video_path)

    # Stage 2: Render mouth shapes + blinks
    blinking_video_path = os.path.join(temp_dir, "blinking.mp4")
    blinks = generate_blink_timings(viseme_data[-1]["end_time"])
    render_stage(screen, resolution, viseme_data, fps, head_image, viseme_images, blink_image, blinks, blinking_video_path)

    # Stage 3: Render mouth shapes + blinks + poses
    final_video_path = output_video
    render_stage(screen, resolution, viseme_data, fps, head_image, viseme_images, blink_image, blinks, final_video_path, pose_data, pose_images)

    print(f"Final video saved to {final_video_path}")


def generate_blink_timings(total_duration):
    """Generate random blink timings."""
    current_time = 0.0
    blinks = []
    while current_time < total_duration:
        blink_start = current_time + random.uniform(2, 7)
        blink_end = blink_start + 0.2
        if blink_end > total_duration:
            break
        blinks.append((blink_start, blink_end))
        current_time = blink_start
    return blinks


def render_stage(screen, resolution, viseme_data, fps, head_image, viseme_images, blink_image, blinks, output_video, pose_data=None, pose_images=None):
    """Render a specific stage of the animation."""
    total_duration = viseme_data[-1]["end_time"]
    total_frames = int(total_duration * fps)
    frame_time = 1 / fps
    current_time = 0.0

    temp_dir = os.path.join(os.path.dirname(output_video), "frames")
    os.makedirs(temp_dir, exist_ok=True)

    for frame_number in tqdm(range(total_frames), desc=f"Rendering {output_video}"):
        # Clear screen
        screen.fill((211, 211, 211))  # Light grey background

        # Draw the head image
        head_x = resolution[0] // 2 - head_image.get_width() // 2
        head_y = resolution[1] // 2 - head_image.get_height() // 2
        screen.blit(head_image, (head_x, head_y))

        # Determine active viseme
        displayed_viseme = "neutral"
        for entry in viseme_data:
            if entry["start_time"] <= current_time < entry["end_time"]:
                displayed_viseme = entry["mouth_shape"]
                break

        if displayed_viseme in viseme_images:
            mouth_image = viseme_images[displayed_viseme]
            mouth_x = head_x + head_image.get_width() // 2 - mouth_image.get_width() // 2
            mouth_y = head_y + head_image.get_height() // 2 - mouth_image.get_height() // 2
            screen.blit(mouth_image, (mouth_x, mouth_y))

        # Add blinking if applicable
        if blink_image and blinks:
            is_blinking = any(start <= current_time < end for start, end in blinks)
            if is_blinking:
                screen.blit(blink_image, (head_x, head_y))

        # Add poses if applicable
        if pose_data and pose_images:
            active_pose = "neutral"
            for entry in pose_data:
                if entry["pose_start_time"] <= current_time < entry["pose_end_time"]:
                    active_pose = entry["pose"]
                    break

            if active_pose in pose_images:
                pose_image = pose_images[active_pose]
                screen.blit(pose_image, (head_x, head_y))

        # Save the frame
        frame_path = os.path.join(temp_dir, f"frame_{frame_number:04d}.png")
        pygame.image.save(screen, frame_path)

        # Increment time
        current_time += frame_time

    # Encode video from frames
    ffmpeg_command = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_video
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Clean up frames
    for frame_file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, frame_file))
    os.rmdir(temp_dir)


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
    mouth_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes"  # Directory containing mouth shape images
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Path to the audio file
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/tmp_frames/"  # Directory to store temporary frames
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/extra_steps_output_video.mp4"  # Video without audio
    final_output = "/Users/nervous/Documents/GitHub/speech-aligner/output/extra_steps_final_output_with_audio.mp4"  # Final video with audio
    head_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/body.png" #body image file
    blink_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/blink.png" #blink image
    pose_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/pose" #pose image folder
    pose_data_path = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json" #pose Data file

    # Configuration
    fps = 30  # Frames per second
    resolution = (800, 600)  # Video resolution

    # Load viseme data
    viseme_data = load_viseme_data(viseme_file)

    # Render animation to video
    render_animation_to_video(viseme_data, mouth_image_path, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, pose_image_path, pose_data_path)

    # Combine video with audio
    combine_audio_with_video(output_video, audio_file, final_output)
