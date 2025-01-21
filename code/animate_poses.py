import re
import random
import pygame
import os
import subprocess
from tqdm import tqdm
import json

def load_viseme_data(viseme_file):
    """Load viseme data from a JSON file."""
    with open(viseme_file, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_transcript_with_poses(transcript, words_timing):
    """
    Parse transcript for poses and generate timing data for each pose.
    """
    # Pose tag regex
    pose_pattern = re.compile(r"<(.*?)>")
    
    # Match pose tags and associate them with timing
    pose_data = []
    for match in re.finditer(pose_pattern, transcript):
        pose = match.group(1)  # Extract pose name
        # Find the word with the closest start time to the pose location
        closest_word = min(
            words_timing, 
            key=lambda x: abs(x['start_time'] - (match.start() / len(transcript)))
        )
        pose_data.append({
            "pose": pose,
            "start_time": closest_word["start_time"],
            "end_time": closest_word["end_time"] + 0.5  # Extend pose duration by 0.5s
        })
    
    return pose_data


def load_file(file_path):
    """Load text or JSON file."""
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file format")


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

    # Load mouth shape images
    mouth_images = {}
    for entry in viseme_data:
        mouth_shape = entry["mouth_shape"]
        if mouth_shape not in mouth_images:
            image_path = os.path.join(mouth_image_dir, mouth_shape)
            if os.path.exists(image_path):
                mouth_images[mouth_shape] = pygame.image.load(image_path)

    # Load pose images, including a required "neutral" pose
    pose_images = {}
    for pose in pose_data:
        pose_name = pose["pose"]
        if pose_name not in pose_images:
            pose_image_path = os.path.join(pose_image_dir, f"{pose_name}.png")
            if os.path.exists(pose_image_path):
                pose_images[pose_name] = pygame.image.load(pose_image_path)

    # Ensure the neutral frame is loaded
    neutral_image_path = os.path.join(mouth_image_dir, "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes/positive/smile.png")
    if os.path.exists(neutral_image_path):
        mouth_images["neutral"] = pygame.image.load(neutral_image_path)
    else:
        raise FileNotFoundError("Neutral frame ('smile.png') not found in the image directory.")

    # Load the neutral pose image
    neutral_image_path = os.path.join(pose_image_dir, "neutral.png")
    if os.path.exists(neutral_image_path):
        pose_images["neutral"] = pygame.image.load(neutral_image_path)
    else:
        raise FileNotFoundError("Neutral pose image (neutral.png) not found in the pose directory.")

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

        # Determine which viseme to show
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
            if pose["start_time"] <= current_time < pose["end_time"]:
                active_pose = pose
                break

        # Render the active pose image, if any
        if active_pose:
            pose_image = pose_images.get(active_pose["pose"])
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


if __name__ == "__main__":
    # File paths
    transcript_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/transcript_poses.txt"
    words_timing_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/word_data.json"
    viseme_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_data.json"
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"
    mouth_image_dir = "/Users/nervous/Documents/GitHub/speech-aligner/assets/visemes"
    pose_image_dir = "/Users/nervous/Documents/GitHub/speech-aligner/assets/pose"
    head_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/body.png"
    blink_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/blink.png"
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/tmp_frames"
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/final_output_with_audio_poses.mp4"
    fps = 30
    resolution = (800, 600)

    # Load data
    transcript = load_file(transcript_file)
    words_timing = load_file(words_timing_file)
    viseme_data = load_file(viseme_file)

    # Parse poses from transcript
    pose_data = parse_transcript_with_poses(transcript, words_timing)

    # Render animation with poses and audio
    render_animation_with_poses(viseme_data, pose_data, mouth_image_dir, pose_image_dir, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, audio_file)
