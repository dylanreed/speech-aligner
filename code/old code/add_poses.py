import cv2
import json
import os
import random

def overlay_poses_on_video(input_video, pose_data_file, output_video, pose_folder):
    """Overlay poses on the video and save as a new video."""
    # Load pose data
    with open(pose_data_file, "r") as f:
        pose_data = json.load(f)

    # Open video
    cap = cv2.VideoCapture(input_video)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # Load poses from the folder
    pose_files = [os.path.join(pose_folder, f) for f in os.listdir(pose_folder) if f.endswith(".png")]

    # Add random poses every 1-7 seconds
    random_pose_timings = []
    total_duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    current_time = 0
    while current_time < total_duration:
        pose_start = current_time + random.uniform(1, 7)
        if pose_start > total_duration:
            break
        pose_end = pose_start + 0.5  # Poses last for 0.5 seconds
        random_pose_timings.append({
            "pose": random.choice(pose_files),
            "pose_start_time": pose_start,
            "pose_end_time": pose_end
        })
        current_time = pose_start

    # Merge predefined poses with random poses
    pose_data.extend(random_pose_timings)

    # Process frames
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Determine if a pose should be overlayed
        current_time = frame_number / fps
        for pose in pose_data:
            if pose['pose_start_time'] <= current_time < pose['pose_end_time']:
                pose_image = cv2.imread(pose['pose'], cv2.IMREAD_UNCHANGED)
                if pose_image is None:
                    print(f"Pose image not found: {pose['pose']}, skipping...")
                    continue
                # Resize pose image to fit within the video frame if necessary
                pose_image = cv2.resize(pose_image, (min(pose_image.shape[1], width), min(pose_image.shape[0], height)), interpolation=cv2.INTER_AREA)
                
                # Overlay pose_image on frame
                x_offset, y_offset = 50, 50  # Example offsets
                y1, y2 = y_offset, y_offset + pose_image.shape[0]
                x1, x2 = x_offset, x_offset + pose_image.shape[1]

                # Adjust overlay region if it exceeds frame boundaries
                y2 = min(y2, frame.shape[0])
                x2 = min(x2, frame.shape[1])
                pose_image = pose_image[:y2-y1, :x2-x1]

                alpha_s = pose_image[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s

                for c in range(3):
                    frame[y1:y2, x1:x2, c] = (alpha_s * pose_image[:, :, c] +
                                               alpha_l * frame[y1:y2, x1:x2, c])

        out.write(frame)
        frame_number += 1

    cap.release()
    out.release()
    print(f"Overlayed video with random poses saved to: {output_video}")

def main():
    """Main function to overlay poses on a video."""
    input_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/animate_final_output_with_audio.mp4"
    pose_data_file = "/Users/nervous/Documents/GitHub/speech-aligner/output/pose_data.json"
    output_video = "/Users/nervous/Documents/GitHub/speech-aligner/output/final_video_with_poses.mp4"
    pose_folder = "/Users/nervous/Documents/GitHub/speech-aligner/assets/pose/"

    if os.path.exists(input_video) and os.path.exists(pose_data_file) and os.path.exists(pose_folder):
        overlay_poses_on_video(input_video, pose_data_file, output_video, pose_folder)
    else:
        print("Input video, pose data file, or pose folder not found.")

if __name__ == "__main__":
    main()
