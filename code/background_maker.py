import cv2
import numpy as np
import cairosvg
from PIL import Image
from io import BytesIO

# Function to render SVG into an image
def render_svg(svg_content, frame_size=(800, 1400)):
    png_bytes = cairosvg.svg2png(bytestring=svg_content, output_width=frame_size[0], output_height=frame_size[1])
    img = Image.open(BytesIO(png_bytes))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# SVG Template with animated paths
svg_template = """
<svg width="100%" height="100%" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <!-- Background Color -->
    <rect width="100%" height="100%" fill="#dac4d0" />

    <!-- Animated Paths -->
    <path fill="#e0829d" fill-opacity="0.7" d="M-100 -100L200 -100L200 {y1}L-100 {y1}Z" 
          transform="rotate({r1}, 50, 0)"/>
    <path fill="#8f5774" fill-opacity="0.7" d="M-100 -100L200 -100L200 {y2}L-100 {y2}Z" 
          transform="rotate({r2}, 50, 0)"/>
    <path fill="#036264" fill-opacity="0.2" d="M-100 -100L200 -100L200 {y3}L-100 {y3}Z" 
          transform="rotate({r3}, 50, 0)"/>
</svg>
"""

# Video Settings
frame_size = (800, 1400)
fps = 30  # Frames per second
duration = 5  # Video duration in seconds
num_frames = fps * duration

# Initialize Video Writer
video_writer = cv2.VideoWriter("/Users/nervous/Documents/GitHub/speech-aligner/output/animated_background.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, frame_size)

print("Generating frames...")

for frame in range(num_frames):
    # Simulating the animations with sine waves for smooth motion
    r1 = -10 + 20 * np.sin(frame * 2 * np.pi / (fps * 5))     # Rotates between -10° and 10° (5s cycle)
    r2 = -30 + 60 * np.sin(frame * 2 * np.pi / (fps * 12.5))  # Rotates between -30° and 30° (12.5s cycle)
    r3 =  40 - 80 * np.sin(frame * 2 * np.pi / (fps * 30))    # Rotates between 40° and -40° (30s cycle)

    y1 = 50 + 10 * np.sin(frame * 0.1)
    y2 = 50 + 15 * np.sin(frame * 0.08)
    y3 = 20 + 20 * np.sin(frame * 0.05)

    # Apply the new values into the SVG template
    svg_frame = svg_template.format(y1=y1, y2=y2, y3=y3, r1=r1, r2=r2, r3=r3)

    # Convert SVG to image and resize
    frame_img = render_svg(svg_frame, frame_size)
    frame_img = cv2.resize(frame_img, frame_size, interpolation=cv2.INTER_AREA)

    # Write frame to video
    video_writer.write(frame_img)

# Finalize Video
video_writer.release()
cv2.destroyAllWindows()

print("🎬 Animated video saved as 'animated_background.mp4'")
