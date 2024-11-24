import cv2
import numpy as np
import os
import sys
import subprocess
import threading
import time

ASCII_CHARS = " .:-=+*#%@"  
VIDEO_FILE = "video.mp4"

WIDTH = 200  
HEIGHT = 50  

def preprocess_frames(video_file):
    frames = []
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_file}")
        return frames

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Processing frames...")

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        resized_frame = cv2.resize(frame, (WIDTH, HEIGHT))
        ascii_art = convert_to_ascii(resized_frame)
        frames.append(ascii_art)

        progress = (i + 1) / frame_count * 100
        sys.stdout.write(f'\rProcessing frames: {progress:.2f}%')
        sys.stdout.flush()

    cap.release()
    print("\nFrame processing completed.")
    return frames

def convert_to_ascii(image):
    height, width, _ = image.shape
    ascii_str = ""

    for y in range(height):
        for x in range(width):
            pixel = image[y, x]

            pixel_sum = int(pixel[0]) + int(pixel[1]) + int(pixel[2])
            brightness = int(pixel_sum / 3)

            ascii_index = brightness // 25  
            ascii_index = min(len(ASCII_CHARS) - 1, ascii_index)  

            ascii_char = ASCII_CHARS[ascii_index]

            color_code = f"\033[38;2;{pixel[2]};{pixel[1]};{pixel[0]}m"
            ascii_str += f"{color_code}{ascii_char}"

        ascii_str += "\033[0m\n"  

    return ascii_str

def play_video_in_command_prompt(frames, fps, start_time):
    frame_interval = 1 / fps
    frame_count = len(frames)
    
    for i in range(frame_count):
        current_time = time.time()
        expected_time = start_time + (i * frame_interval)
        sleep_time = expected_time - current_time

        if sleep_time > 0:
            time.sleep(sleep_time)
        
        sys.stdout.write('\033[H')  
        sys.stdout.write(frames[i])  
        sys.stdout.flush()

def play_video_in_window():
    try:
        if os.name == 'nt':
            subprocess.Popen(['start', VIDEO_FILE], shell=True)
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', VIDEO_FILE])
        else:
            print("Unsupported OS")
            return
    except Exception as e:
        print(f"Error opening video file: {e}")

def process_video():
    global frames, fps
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
    try:
        if os.path.isfile(VIDEO_FILE):
            processing_thread = threading.Thread(target=process_video)
            processing_thread.start()
            processing_thread.join()

            video_window_thread = threading.Thread(target=play_video_in_window)
            video_window_thread.start()

            time.sleep(1)

            start_time = time.time()
            play_video_in_command_prompt(frames, fps, start_time)

            video_window_thread.join()

            print("Playback finished. Exiting...")
        else:
            print(f"No video file named {VIDEO_FILE} found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
