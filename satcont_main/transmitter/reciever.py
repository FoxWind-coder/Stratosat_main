import serial
import os
import json
import time
import binascii

def send_ready(port, baudrate):
    ser = serial.Serial('/dev/ttyS{}'.format(port), baudrate)
    while True:
        ser.write(b'reajhjhy\n')
        time.sleep(1)

def receive_file(port, baudrate):
    ser = serial.Serial('/dev/ttyS{}'.format(port), baudrate)
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().strip()
            if data.startswith(b'sendjson'):
                _, crc = data.split()
                crc = int(crc)
                ser.write(b'ok\n')
                break

    received_data = b''
    while True:
        data = ser.read()
        if data == b'':
            break
        received_data += data

    received_crc = binascii.crc32(received_data)
    if received_crc == crc:
        ser.write(b'done\n')
        return received_data
    else:
        ser.write(b'repeat\n')
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Receive file over serial port from Windows.')
    parser.add_argument('port', type=int, help='Serial port number (e.g., for ttyS1, use 1)')
    parser.add_argument('baudrate', type=int, help='Baudrate of the serial connection')
    args = parser.parse_args()

    send_ready(args.port, args.baudrate)
    file_content = receive_file(args.port, args.baudrate)
    if file_content is not None:
        with open('received_tree.json', 'wb') as f:
            f.write(file_content)
        print('File received successfully.')
    else:
        print('Error receiving file.')
