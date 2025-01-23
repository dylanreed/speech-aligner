from tqdm import tqdm
import pygame
import json
import os
import subprocess
import random
import shutil

def load_viseme_data(viseme_file):
    """Load viseme data from a JSON file."""
    with open(viseme_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_pose_data(pose_data):
    """Load pose data from a JSON file and validate its structure."""
    with open(pose_data, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("pose_data should be a list of dictionaries")
        # Validate each entry in the pose_data
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError(f"Invalid pose data entry: {entry}")
            required_keys = ["pose_image", "pose_start_time", "pose_end_time"]
            for key in required_keys:
                if key not in entry:
                    raise ValueError(f"Missing key '{key}' in pose data entry: {entry}")
        return data

def render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, pose_folder, pose_data, viseme_size):
    """Render animation frames and encode them into a video, with blinks and random poses."""
    pygame.init()

    # Set up display (off-screen rendering)
    screen = pygame.Surface(resolution)

    # Load images #

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

    # Load and resize viseme images
    viseme_images = {}
    for entry in viseme_data:
        mouth_shape = entry["mouth_shape"]
        if mouth_shape not in viseme_images:
            image_path = os.path.join(image_directory, mouth_shape)
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                viseme_images[mouth_shape] = pygame.transform.scale(image, viseme_size)  # Resize viseme

    # Ensure the neutral viseme frame is loaded
    neutral_viseme_path = os.path.join(image_directory, "neutral.png")
    if os.path.exists(neutral_viseme_path):
        neutral_image = pygame.image.load(neutral_viseme_path)
        viseme_images["neutral"] = pygame.transform.scale(neutral_image, viseme_size)  # Resize neutral viseme
    else:
        raise FileNotFoundError("Neutral viseme ('neutral.png') not found in the viseme directory.")

    # Load pose images
    pose_images = {}
    for entry in pose_data:
        if isinstance(entry, dict) and "pose_image" in entry:
            pose = entry["pose_image"]
            if pose not in pose_images:
                pose_image_path = os.path.join(pose_folder, pose)
                if os.path.exists(pose_image_path):
                    pose_images[pose] = pygame.image.load(pose_image_path)

    # Ensure temp directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Generate random blink timings
    total_duration = viseme_data[-1]["end_time"]
    current_time = 0.0
    blinks = []
    while current_time < total_duration:
        blink_start = current_time + random.uniform(2, 10)
        blink_end = blink_start + 0.2
        if blink_end > total_duration:
            break
        blinks.append((blink_start, blink_end))
        current_time = blink_start

    # Render frames
    total_frames = int(viseme_data[-1]["end_time"] * fps)
    frame_time = 1 / fps
    current_time = 0.0

    print(f"Rendering {total_frames} frames...")
    for frame_number in tqdm(range(total_frames), desc="Rendering Frames"):
        # Clear screen
        screen.fill((211, 211, 211))

        # Render head
        head_x = resolution[0] // 2 - head_image.get_width() // 2
        head_y = resolution[1] // 2 - head_image.get_height() // 2
        screen.blit(head_image, (head_x, head_y))

        # Determine which viseme to show
        displayed_viseme = "neutral"  # Default to neutral viseme
        for entry in viseme_data:
            viseme_start = entry["start_time"]
            viseme_end = entry["end_time"]
            mouth_shape = entry["mouth_shape"]

            if viseme_start <= current_time < viseme_end:
                displayed_viseme = mouth_shape
                break

        # Display the selected viseme (neutral if no active viseme)
        if displayed_viseme in viseme_images:
            mouth_image = viseme_images[displayed_viseme]
            mouth_x = head_x + head_image.get_width() // 2 - mouth_image.get_width() // 2
            mouth_y = head_y + head_image.get_height() // 2 - mouth_image.get_height() // 2
            screen.blit(mouth_image, (mouth_x, mouth_y))

        # Increment time
        current_time += frame_time

        # Save the frame as an image
        frame_path = os.path.join(temp_dir, f"frame_{frame_number:04d}.png")
        pygame.image.save(screen, frame_path)

    # Encode frames to video
    ffmpeg_command = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", f"{temp_dir}/frame_%04d.png",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_video
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"Video saved to {output_video}")

    # Clean up temporary frames
    try:
        shutil.rmtree(temp_dir)
        print(f"Temporary frames in {temp_dir} deleted.")
    except Exception as e:
        print(f"Error deleting temporary frames: {e}")

if __name__ == "__main__":
    viseme_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_data.json"
    image_directory = "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes"
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/tmp_frames/frames"
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/poses_animate_output_video.mp4"
    head_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/body.png"
    blink_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/blink.png"
    fps = 30
    resolution = (800, 600)
    viseme_size = (128, 70)  # Desired size for viseme images (width, height)

    # Load data
    viseme_data = load_viseme_data(viseme_file)

    render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, None, [], viseme_size)
