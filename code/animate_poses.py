
from tqdm import tqdm
import pygame
import json
import os
import subprocess
import random


def load_file(file_path):
    """
    Load text or JSON file content.
    Args:
        file_path (str): Path to the file.
    Returns:
        str or dict: File content (string for text files, dict for JSON files).
    """
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file format for file: {file_path}")

def load_viseme_data(viseme_file):
    """Load viseme data from a JSON file."""
    with open(viseme_file, "r", encoding="utf-8") as f:
        return json.load(f)
    


def render_animation_with_poses(viseme_data, pose_data, mouth_image_dir, pose_image_dir, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, audio_file):
    """Render animation frames with head, mouth shapes, blinking, poses, and add audio to the final video."""
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
    
    # Load blink image
    if os.path.exists(blink_image_path):
        blink_image = pygame.image.load(blink_image_path)
    else:
        raise FileNotFoundError(f"Blink image not found: {blink_image_path}")

    # Load mouth shape images from assets/visemes/positive
    mouth_images = {}
    mouth_image_dir = os.path.join("/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes/positive")
    for file_name in os.listdir(mouth_image_dir):
        if file_name.endswith(".png"):
            mouth_shape = file_name.replace(".png", "")  # Remove the file extension
            image_path = os.path.join(mouth_image_dir, file_name)
            mouth_images[mouth_shape] = pygame.image.load(image_path)

    # Load pose images
    pose_images = {}
    for file_name in os.listdir(pose_image_dir):
        if file_name.endswith(".png"):
            pose_name = file_name.replace(".png", "")  # Remove the file extension
            image_path = os.path.join(pose_image_dir, file_name)
            pose_images[pose_name] = pygame.image.load(image_path)

    # Ensure neutral pose exists
    neutral_image_path = os.path.join(pose_image_dir, "neutral.png")
    if os.path.exists(neutral_image_path):
        pose_images["neutral"] = pygame.image.load(neutral_image_path)
    else:
        raise FileNotFoundError(f"Neutral pose image not found: {neutral_image_path}")

    # Ensure temp directory exists

    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Generate random blink timings
    total_duration = viseme_data[-1]["end_time"]
    current_time = 0.0
    blinks = []
    while current_time < total_duration:
        blink_start = current_time + random.uniform(2, 7)  # Random interval between 2-7 seconds
        blink_end = blink_start + 0.2  # Blink duration of 0.2 seconds
        if blink_end > total_duration:
            break
        blinks.append((blink_start, blink_end))
        current_time = blink_start

    # Render frames
    total_frames = int(total_duration * fps)
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

        # Determine which viseme to show (fallback to "neutral" mouth shape if none is active)
        displayed_image = "neutral"
        for entry in viseme_data:
            viseme_start = entry["start_time"]
            viseme_end = entry["end_time"]
            mouth_shape = entry["mouth_shape"]

            if viseme_start <= current_time < viseme_end:
                displayed_image = mouth_shape
                break

        # Draw the selected mouth shape
        if displayed_image in mouth_images:
            mouth_image = mouth_images[displayed_image]
            mouth_x = head_x + head_image.get_width() // 2 - mouth_image.get_width() // 2
            mouth_y = head_y + head_image.get_height() // 2 - mouth_image.get_height() // 2
            screen.blit(mouth_image, (mouth_x, mouth_y))

        # Check if the current frame is during a blink
        is_blinking = any(blink_start <= current_time < blink_end for blink_start, blink_end in blinks)
        if is_blinking:
            screen.blit(blink_image, (head_x, head_y))

        # Determine the active pose for the current frame
        active_pose = None
        for pose in pose_data:
            if isinstance(pose, dict) and "start_time" in pose and "end_time" in pose:
                if pose["start_time"] <= current_time < pose["end_time"]:
                    active_pose = pose
                    break
                    
        # Render the active pose or the neutral pose
        pose_image = None
        if active_pose and active_pose["pose"] in pose_images:
            pose_image = pose_images[active_pose["pose"]]
        elif "neutral" in pose_images:
            pose_image = pose_images["neutral"]

        if pose_image:
            screen.blit(pose_image, (head_x, head_y))

        # Save the frame as an image
        frame_path = os.path.join(temp_dir, f"frame_{frame_number:04d}.png")
        pygame.image.save(screen, frame_path)

        # Increment time
        current_time += frame_time

    # Encode frames to video
    print("Encoding video...")
    temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
    ffmpeg_command = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", temp_video_path
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Combine video with audio
    print("Adding audio to video...")
    final_output_path = output_video
    ffmpeg_command = [
        "ffmpeg", "-y", "-i", temp_video_path, "-i", audio_file,
        "-c:v", "copy", "-c:a", "aac", "-shortest", final_output_path
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"Final video with audio saved to {final_output_path}")


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
    mouth_image_dir = "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes/positive"  # Directory containing mouth shape images
    pose_image_dir = "/Users/nervous/Documents/GitHub/speech-aligner/assets/pose" #path to poses
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"  # Path to the audio file
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/temp_frames/"  # Directory to store temporary frames
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_video.mp4"  # Video without audio
    final_output = "/Users/nervous/Documents/GitHub/speech-aligner/output/final_output_with_audio.mp4"  # Final video with audio
    head_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/body.png" #head image
    blink_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/blink.png" #blink image
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript_poses.txt" #transcript with poses
    words_timing_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/word_data.json" #word timings
    pose_data_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"

    # Configuration
    fps = 30  # Frames per second
    resolution = (800, 600)  # Video resolution

    # Load data
    transcript = load_file(transcript_file)
    words_timing = load_file(words_timing_file)
    viseme_data = load_file(viseme_file)

    # Render animation with poses and audio
    render_animation_with_poses(
        viseme_data=viseme_data,
        pose_data=pose_data_file,
        mouth_image_dir=mouth_image_dir,
        pose_image_dir=pose_image_dir,
        output_video=output_video,
        fps=fps,
        resolution=resolution,
        temp_dir=temp_dir,
        head_image_path=head_image_path,
        blink_image_path=blink_image_path,
        audio_file=audio_file
    )