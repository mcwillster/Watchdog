import pyautogui
from pathlib import Path
from datetime import datetime
import os
import socket
import struct
import io
from PIL import Image


SERVER_IP = "127.0.0.1"
PORT = 7777
CHUNK_SIZE = 1400  #Max size is 1500, go a little lower to be safe
TIMEOUT = 0.04
FOLDER_PATH = Path("C:/Totally Legit Files")


def screenshot():
    FOLDER_PATH.mkdir(parents=False, exist_ok=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    now = datetime.now()
    file_name = "screenshot" + now.strftime('%Y-%m-%d_%H-%M-%S') +".png"
    file_path = FOLDER_PATH / file_name
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    print(f"Loading and optimizing {screenshot} with Pillow...")

    if screenshot.mode in ("RGBA", "P"):
        screenshot = screenshot.convert("RGB")

    buffer = io.BytesIO()
    screenshot.save(buffer, format="JPEG", quality=85, optimize=True)
    image_bytes = buffer.getvalue()
    total_bytes = len(image_bytes)
    print(f"Compressed size: {total_bytes} bytes (Ready for transmission).")
    byte_pointer = 0
    seq_num = 0
    while True:
        chunk = image_bytes[byte_pointer:byte_pointer + CHUNK_SIZE]
        byte_pointer += CHUNK_SIZE
        is_eof = 1 if byte_pointer >= total_bytes else 0
        header = struct.pack("!IB", seq_num, is_eof)
        packet = header + chunk
        while True:
            try:
                sock.sendto(packet, (SERVER_IP, PORT))
            
                # Listen for receipt acknowledgement
                ack_packet, _ = sock.recvfrom(10)
                ack_seq, = struct.unpack("!I", ack_packet)
            
                if ack_seq == seq_num:
                    break  # Confirmed, move to next packet
            except socket.timeout:
                pass  # Drop hit, loop immediately repeats and triggers resend
            
        if is_eof:
            print(f"Photo sent successfully across {seq_num + 1} UDP packets.")
            break
        
        seq_num += 1

    sock.close()


def main():
    print("Watchdog V0.1, type HELP for help\n")
    screenshot()
        

if __name__ == "__main__":
    main()