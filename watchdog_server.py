from pathlib import Path
import socket
import struct
import io
from PIL import Image
import threading
import time


FOLDER_PATH = Path.cwd()
OUTPUT_PHOTO = "received_photo.jpg"
HOST='127.0.0.1'
PORT='7777'


def init_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Watchdog Server listening on {HOST}:{PORT}...")
    while True:
        expected_seq = 0
        photo_stream = bytearray()
        while True:
            try:
                packet, addr = sock.recvfrom(2048)
                header = packet[:5]
                chunk = packet[5:]
                seq_num, is_eof = struct.unpack("!IB", header)

                if seq_num == expected_seq:
                    photo_stream.extend(chunk)

                    ack_packet = struct.pack("!I", seq_num)
                    sock.sendto(ack_packet, addr)

                    if is_eof == 1:
                        break
                    expected_seq += 1
                elif (seq_num < expected_seq):
                    # Resend ACK for duplicate packets
                    ack_packet = struct.pack("!I", seq_num)
                    sock.sendto(ack_packet, addr)
            except Exception:
                continue
        try:
            img_buffer = io.BytesIO(photo_stream)
            received_image = Image.open(img_buffer)
            received_image.save(OUTPUT_PHOTO)
        
            # Print a message directly into the terminal window
            print(f"\n[NETWORK] New photo saved to {OUTPUT_PHOTO}")
            print("Watchdog > ", end="", flush=True) # Reprint prompt line cleanly
        except Exception as e:
            print(f"\n[NETWORK] Failed to parse received photo data: {e}")

def main():
    print("Watchdog Server V0.1, type HELP for help\n")
    while (True):
        command = input("Watchdog >").strip().lower()
        match command:
            case "help":
                print("womp womp, help not implimented")
            case "init":
                global HOST
                global PORT
                host = input("Enter Host IP (leave blank for localhost) >")
                port = int(input("Enter Host Port (leave blank for 7777) >"))
                HOST = HOST if host == "" else host
                PORT = PORT if port == "" else port
                network_thread = threading.Thread(target=init_server, daemon=True)
                network_thread.start()
                time.sleep(.5)
            case "change path":
                input_path = input("Enter Desired Path >")
                global FOLDER_PATH
                FOLDER_PATH = Path(input_path)
            case "exit" | "break":
                break
            case _:
                print("Try Again")
        

if __name__ == "__main__":
    main()