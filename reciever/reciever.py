# -*- coding: utf-8 -*-

import serial
import sys
import os

def receive_file(save_path, port, baudrate):
    try:
        with serial.Serial(port, baudrate) as ser:
            print("Waiting for data...")
            buffer = b''
            start_marker = b'++'
            end_marker = b'++'
            
            # Read until start marker is found
            while True:
                byte = ser.read(1)
                buffer += byte
                if start_marker in buffer:
                    buffer = buffer.split(start_marker, 1)[1]
                    print("Start marker detected.")
                    break
            
            # Read until end marker is found
            while True:
                byte = ser.read(1)
                buffer += byte
                if end_marker in buffer:
                    buffer = buffer.split(end_marker, 1)[0]
                    print("End marker detected.")
                    break

            print("Data received!")

        # Generate the filename
        file_count = len([name for name in os.listdir(save_path) if name.startswith("splash_") and name.endswith(".pix")])
        new_file_name = "splash_{}.pix".format(file_count + 1)
        new_file_path = os.path.join(save_path, new_file_name)

        # Save the data to a file with explicit UTF-8 encoding
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(buffer.decode('utf-8'))
            print("File saved as {}.".format(new_file_name))

    except Exception as e:
        print("An error occurred: {}".format(e))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python receiver.py <save_path> <port> <baudrate>")
        sys.exit(1)

    save_path = sys.argv[1]
    port = sys.argv[2]
    baudrate = int(sys.argv[3])

    # Check if the directory exists
    if not os.path.exists(save_path):
        print("Error: The directory {} does not exist.".format(save_path))
        sys.exit(1)

    receive_file(save_path, port, baudrate)
