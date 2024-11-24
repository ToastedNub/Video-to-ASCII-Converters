import cv2
import numpy as np
import os
import pygame
import time

ASCII_CHARS = " .:-=+*#%@"
VIDEO_FILE = "video.mp4"

WIDTH = 230
HEIGHT = 125
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

TARGET_FPS = 15

playback_speed = 0.25

def preprocess_frames(video_file):
    frames = []
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_file}")
        return frames

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Processing frames...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (WIDTH, HEIGHT))
        ascii_art = convert_to_ascii(resized_frame)
        frames.append(ascii_art)

        percent = (len(frames) / frame_count) * 100
        print(f"\rProcessing... {percent:.2f}%", end="")

    cap.release()
    print("\nFrame processing completed.")
    return frames

def convert_to_ascii(image):
    height, width, _ = image.shape
    ascii_str = []
    
    for y in range(height):
        row = []
        for x in range(width):
            pixel = image[y, x]
            r, g, b = pixel[2], pixel[1], pixel[0]
            brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
            ascii_index = brightness // 25
            ascii_index = min(len(ASCII_CHARS) - 1, ascii_index)
            ascii_char = ASCII_CHARS[ascii_index]
            row.append((ascii_char, r, g, b))
        ascii_str.append(row)

    return ascii_str

def play_video_in_pygame(frames, fps):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("ASCII Art Video Playback")

    font = pygame.font.SysFont("Courier", 12)
    clock = pygame.time.Clock()

    frame_count = len(frames)
    frame_interval = (1 / fps) * playback_speed

    start_time = time.time()
    running = True
    frame_index = 0
    while running and frame_index < frame_count:
        clock.tick(TARGET_FPS)

        current_time = time.time()
        elapsed_time = current_time - start_time
        expected_time = frame_index * frame_interval

        if elapsed_time < expected_time:
            pygame.time.delay(int((expected_time - elapsed_time) * 1000))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        ascii_art = frames[frame_index]
        y_offset = 0

        ascii_surface = pygame.Surface((WIDTH * 8, HEIGHT * 8))
        for row in ascii_art:
            x_offset = 0
            for char, r, g, b in row:
                color = (r, g, b)
                text_surface = font.render(char, True, color)
                ascii_surface.blit(text_surface, (x_offset, y_offset))
                x_offset += 8
            y_offset += 8

        screen.blit(ascii_surface, (0, 0))
        pygame.display.flip()
        frame_index += 1

    pygame.quit()

def process_video():
    global frames, fps
    frames = []
    try:
        frames = preprocess_frames(VIDEO_FILE)
        if not frames:
            print(f"Error processing video file {VIDEO_FILE}")
            return
        
        cap = cv2.VideoCapture(VIDEO_FILE)
        if not cap.isOpened():
            print(f"Error: Unable to open video file {VIDEO_FILE}")
            return
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
    except Exception as e:
        print(f"Error processing video: {e}")

def main():
    global frames
    try:
        if os.path.isfile(VIDEO_FILE):
            process_video()
            if frames:
                play_video_in_pygame(frames, fps)
            else:
                print("No frames to display. Exiting...")

            print("Playback finished. Exiting...")
        else:
            print(f"No video file named {VIDEO_FILE} found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()