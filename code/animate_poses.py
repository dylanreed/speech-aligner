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

def render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, pose_folder, pose_data, background_path):
    """Render animation frames and encode them into a video, with blinks and random poses."""
    # Debug: print loaded pose_data
    print("Pose data at the start of render_animation_to_video:")
    for entry in pose_data:
        print(entry)  # Log the content of pose_data
    pygame.init()

    # Set up display (off-screen rendering)
    screen = pygame.Surface(resolution)

    # Load images #
    # Load Background Image
    bg_image = pygame.image.load(background_path)
    bg_image = pygame.transform.scale(bg_image, resolution)  # Scale background to fit the screen

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

    # Load viseme images
    viseme_images = {}
    for entry in viseme_data:
        mouth_shape = entry["mouth_shape"]
        if mouth_shape not in viseme_images:
            image_path = os.path.join(image_directory, mouth_shape)
            if os.path.exists(image_path):
                viseme_images[mouth_shape] = pygame.image.load(image_path)

    # Ensure the neutral viseme frame is loaded
    neutral_viseme_path = os.path.join(image_directory, "neutral.png")
    if os.path.exists(neutral_viseme_path):
        viseme_images["neutral"] = pygame.image.load(neutral_viseme_path)
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
                else:
                    print(f"Pose image not found for pose: {pose}")

    # Check for missing neutral pose image
    neutral_pose_path = os.path.join(pose_folder, "neutralpose.png")
    if not os.path.exists(neutral_pose_path):
        print("Warning: Neutral pose ('neutralpose.png') not found in the pose directory.")
    else:
        pose_images["neutralpose"] = pygame.image.load(neutral_pose_path)
      
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
        screen.blit(bg_image, (0, 0))  # Draw the background
        #screen.fill((211, 211, 211))

        # Render head
        #head_x = resolution[0] // 2 - head_image.get_width() // 2
        #head_y = resolution[1] // 2 - head_image.get_height() // 2
        #screen.blit(head_image, (head_x, head_y))

         # Adjust positions
        head_x = resolution[0] // 2 - head_image.get_width() // 2
        head_y = resolution[1] // 2 - head_image.get_height() // 2 + resolution[1] // 4  # Move down 25%
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

        # Determine which pose to show
        displayed_pose = "neutralpose"  # Default to neutral viseme
        for entry in pose_data:
            pose_start = entry["pose_start_time"]
            pose_end = entry["pose_end_time"]
            pose_image = entry["pose_image"]

            if pose_start <= current_time < pose_end:
                displayed_pose = pose_image
                break

        # Display the selected pose (neutral if no active viseme)
        if displayed_pose in pose_images:
            pose_image = pose_images[displayed_pose]
            pose_x = head_x + head_image.get_width() // 2 - pose_image.get_width() // 2
            pose_y = head_y + head_image.get_height() // 2 - pose_image.get_height() // 2
            screen.blit(pose_image, (pose_x, pose_y))

        # Check if the current frame is during a blink
        is_blinking = any(blink_start <= current_time < blink_end for blink_start, blink_end in blinks)
        if is_blinking:
            screen.blit(blink_image, (head_x, head_y))

        # Save the frame as an image
        frame_path = os.path.join(temp_dir, f"frame_{frame_number:04d}.png")
        pygame.image.save(screen, frame_path)

        # Increment time
        current_time += frame_time


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
    viseme_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/viseme_data.json"
    image_directory = "/Users/nervous/Documents/GitHub/speech-aligner/assets/new_visemes"
    audio_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/output_audio.wav"
    temp_dir = "/Users/nervous/Documents/GitHub/speech-aligner/tmp_frames/frames"
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/poses_animate_output_video.mp4"
    final_output = "/Users/nervous/Documents/GitHub/speech-aligner/output/poses_animate_final_output_with_audio.mp4"
    head_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/norris_body.png"
    blink_image_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/other/norris_blink.png"
    pose_folder = "/Users/nervous/Documents/GitHub/speech-aligner/assets/pose/"
    pose_data = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"
    fps = 30
    resolution = (1320, 2868)

    # Load data
    viseme_data = load_viseme_data(viseme_file)
    pose_data = load_pose_data(pose_data)  # Call load_pose_data to parse JSON
    background_path = "/Users/nervous/Documents/GitHub/speech-aligner/assets/background/background.png"

    render_animation_to_video(viseme_data, image_directory, output_video, fps, resolution, temp_dir, head_image_path, blink_image_path, pose_folder, pose_data, background_path)

    combine_audio_with_video(output_video, audio_file, final_output)
