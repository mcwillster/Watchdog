from pathlib import Path
import socket
import struct
import io
from PIL import Image
import threading
import time
from art import tprint


FOLDER_PATH = Path.cwd() #set to project path, changable with change-path command
OUTPUT_PHOTO = "received_photo.jpg" #file name
HOST='127.0.0.1'
PORT='7777'

#Thread function for the server running and all network processes
def init_server():

    #server setup stuff
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Watchdog Server listening on {HOST}:{PORT}...")

    #constant loop to setup and check for new files coming in
    while True:

        #sets variables for the expected packet sequence and the photo bytes
        expected_seq = 0
        photo_stream = bytearray()

        #loop to recieve file
        while True:
            try:
                packet, addr = sock.recvfrom(2048)#this function/thread will just wait on this command until it recieves the first packet of a photo. THIS MIGHT BE A PROBLEM LATER
                header = packet[:5]#takes first five elements/bytes and stores them as header
                chunk = packet[5:]#stores rest of elements as actual data
                seq_num, eof = struct.unpack("!IB", header) #splits header into seq number and eof flag


                if seq_num == expected_seq:
                    photo_stream.extend(chunk)

                    #make ack packet and send
                    ack_packet = struct.pack("!I", seq_num)
                    sock.sendto(ack_packet, addr)

                    #if end of file, end file, duh
                    if eof == 1:
                        break

                    expected_seq += 1

                elif (seq_num < expected_seq):
                    # Resend acknowledgement for duplicate packets
                    ack_packet = struct.pack("!I", seq_num)
                    sock.sendto(ack_packet, addr)

            #exceptions arent real, they can't hurt you
            except Exception:
                continue
        try:
            #convert bytes into an actual image
            img_buffer = io.BytesIO(photo_stream)
            received_image = Image.open(img_buffer)
            received_image.save(OUTPUT_PHOTO)
            print(f"\n[NETWORK] New photo saved to {OUTPUT_PHOTO}")

            print("Watchdog > ", end="", flush=True) # Reprint prompt line
        except Exception as e:
            print(f"\n[NETWORK] Failed to parse received photo data: {e}")

def main():
    tprint("~Watchdog~") #"cool" ascii art
    print("Watchdog Server V0.1, type HELP for help\n")

    #loop for cli
    while (True):

        command = input("Watchdog >").strip().lower()
        match command:

            case "help":
                print("womp womp, help not implimented")

            case "init":
                #set host and port
                global HOST
                global PORT
                host = input("Enter Host IP (leave blank for localhost) >")
                port = input("Enter Host Port (leave blank for 7777) >")
                HOST = HOST if host == "" else host
                PORT = int(PORT) if port == "" else int(port)
            
                #start thread to receive photo
                network_thread = threading.Thread(target=init_server, daemon=True)
                network_thread.start()
                time.sleep(.5)

            case "change-path":
                input_path = input("Enter Desired Path >")
                global FOLDER_PATH
                FOLDER_PATH = Path(input_path)

            case "exit" | "break":
                break

            case _:
                print("Try Again")
        

if __name__ == "__main__":
    main()