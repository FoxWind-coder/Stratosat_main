# -*- coding: utf-8 -*-

import serial
import json
import sys
import os

def read_json_file(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['converted_file']

def transmit_file(port, baudrate, json_path):
    # Чтение содержимого JSON файла
    file_path = read_json_file(json_path)

    # Чтение данных из файла с явным указанием кодировки UTF-8
    with open(file_path, 'r', encoding='utf-8') as f:
        file_data = f.read()

    # Преобразование данных в байты и добавление маркеров начала и конца
    data_to_send = b'++' + file_data.encode('utf-8') + b'++'

    # Передача данных через UART
    with serial.Serial(port, baudrate) as ser:
        ser.write(data_to_send)
        print("Data sent.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python transmitter.py <port> <baudrate> <json_path>")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2])
    json_path = sys.argv[3]

    # Проверка наличия файла JSON
    if not os.path.isfile(json_path):
        print("Error: The file {} does not exist.".format(json_path))
        sys.exit(1)

    transmit_file(port, baudrate, json_path)
