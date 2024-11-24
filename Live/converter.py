import cv2
import numpy as np
import sys
import time
import mss
from PIL import Image

ASCII_CHARS = " .:-=+*#%@"  
WIDTH = 200  
HEIGHT = 50  

def rgb_to_ansi(r, g, b):
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
        img = img.resize((WIDTH, HEIGHT))
        return np.array(img)

def convert_to_ascii(image):
    height, width, _ = image.shape
    ascii_str = ""

    for y in range(height):
        for x in range(width):
            pixel = image[y, x]
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

            pixel_sum = r + g + b
            brightness = int(pixel_sum / 3)
            ascii_index = brightness // 25  
            ascii_index = min(len(ASCII_CHARS) - 1, ascii_index)  

            ascii_char = ASCII_CHARS[ascii_index]

            color_code = f"\033[38;5;{rgb_to_ansi(r, g, b)}m"
            ascii_str += f"{color_code}{ascii_char}"

        ascii_str += "\033[0m\n"  

    return ascii_str

def play_screen_in_command_prompt():
    frame_time = 1 / 60
    while True:
        start_time = time.time()

        frame = capture_screen()
        ascii_art = convert_to_ascii(frame)

        sys.stdout.write('\033[H')
        sys.stdout.write(ascii_art)
        sys.stdout.flush()

        elapsed_time = time.time() - start_time
        time.sleep(max(0, frame_time - elapsed_time))

def main():
    try:
        print("Starting live screen capture at 60 FPS...")
        play_screen_in_command_prompt()
    except KeyboardInterrupt:
        print("\nScreen capture stopped. Exiting...")

if __name__ == "__main__":
    main()
