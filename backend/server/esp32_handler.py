"""
esp32_handler.py

Two helper functions:
- save_image_from_post(file_bytes, save_path): save incoming multipart image upload from esp32
- read_images_from_serial(port, baudrate, save_path_prefix): a helper to read JPEG frames over serial if you implemented a framing protocol

ESP32 can either:
1) POST images to backend /upload endpoint (recommended)
2) Send raw JPEG binary via serial; use `read_images_from_serial` to capture and save.
"""

import os
from pathlib import Path

def save_image_from_post(file_bytes, save_path):
    """
    Save raw image bytes (from a POST) to disk.
    """
    p = Path(save_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        f.write(file_bytes)
    return str(p)

# Simple serial reading helper (very minimal). On the ESP32 you should wrap frames with start/end markers.
def read_images_from_serial(serial_port, baudrate, out_dir, start_marker=b"<IMG>", end_marker=b"</IMG>"):
    """
    Read framed images from serial and save them. This function blocks and loops.
    The ESP32 must send frames like: <IMG>...jpeg bytes...</IMG>
    """
    import serial
    import time
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ser = serial.Serial(serial_port, baudrate, timeout=1)
    buf = b""
    frame_id = 0
    try:
        while True:
            data = ser.read(4096)
            if not data:
                time.sleep(0.01)
                continue
            buf += data
            while True:
                start = buf.find(start_marker)
                end = buf.find(end_marker)
                if start != -1 and end != -1 and end > start:
                    img_bytes = buf[start+len(start_marker):end]
                    out_path = Path(out_dir) / f"frame_{frame_id:06d}.jpg"
                    with open(out_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"Saved {out_path}")
                    frame_id += 1
                    buf = buf[end+len(end_marker):]
                else:
                    break
    finally:
        ser.close()
