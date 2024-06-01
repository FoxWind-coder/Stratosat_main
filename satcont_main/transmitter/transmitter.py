import serial
import sys
import os
import hashlib

def calculate_crc(filename):
    with open(filename, "rb") as f:
        data = f.read()
    crc = hashlib.md5(data).hexdigest()
    return crc

def send_file(port, baudrate, timeout, chunk_size, folder):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        ser.flush()

        # Send tree.json
        ser.write(b"ready\n")
        time.sleep(0.1)  # Add delay to ensure receiver is ready
        ser.write(f"fl temp/tree.json {calculate_crc(os.path.join(folder, 'temp', 'tree.json'))}\n".encode("utf-8"))
        with open(os.path.join(folder, "temp", "tree.json"), "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                ser.write(chunk + b"\n")
        ser.write(b"endfile\n")
        while True:
            response = ser.readline().decode("utf-8").rstrip()
            if response == "ok":
                break
            elif response == "repeat":
                # Handle repeat transmission
                continue

        # Send other files
        for root, _, files in os.walk(folder):
            for filename in files:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, folder)
                ser.write(b"ready\n")
                ser.write(f"fl {rel_path} {calculate_crc(filepath)}\n".encode("utf-8"))
                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        ser.write(chunk + b"\n")
                ser.write(b"endfile\n")
                while True:
                    response = ser.readline().decode("utf-8").rstrip()
                    if response == "ok":
                        break
                    elif response == "repeat":
                        # Handle repeat transmission
                        continue

    except serial.SerialException as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python sender.py <port> <baudrate> <timeout> <chunk_size> <folder>")
        sys.exit(1)
    port = sys.argv[1]
    baudrate = int(sys.argv[2])
    timeout = int(sys.argv[3])
    chunk_size = int(sys.argv[4])
    folder = sys.argv[5]

    send_file(port, baudrate, timeout, chunk_size, folder)
