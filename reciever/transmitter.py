import serial
import time
import os
import sys

def send_file(port, baudrate, filepath):
    ser = serial.Serial(port, baudrate, timeout=1)
    ser.flush()

    # Чтение файла и разбивка его на пакеты
    with open(filepath, 'rb') as file:
        data = file.read()
    
    file_size = len(data)
    packet_size = 240  # Размер пакета данных (LoRa E32 имеет ограничение на пакет данных)
    num_packets = (file_size + packet_size - 1) // packet_size
    
    ser.write(f"SIZE:{file_size}\n".encode())
    time.sleep(1)
    
    for i in range(num_packets):
        start = i * packet_size
        end = start + packet_size
        packet = data[start:end]
        ser.write(packet)
        time.sleep(0.5)  # Задержка для обеспечения надежной передачи

        # Ожидание подтверждения
        ack = ser.readline().decode().strip()
        while ack != 'ACK':
            ser.write(packet)
            time.sleep(0.5)
            ack = ser.readline().decode().strip()
    
    ser.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <port> <baudrate> <filepath>")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2])
    filepath = sys.argv[3]

    send_file(port, baudrate, filepath)
