import sys
import serial
import json
import os
import hashlib
import time
import logging

def calculate_checksum(file_path):
    """Вычисляет контрольную сумму файла"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

def send_file(file_path, serial_port):
    """Отправляет файл через COM порт"""
    with open(file_path, 'rb') as file:
        data = file.read()
        serial_port.write(data)

def send_folder(folder_path, serial_port, port_settings):
    """Отправляет содержимое папки через COM порт"""
    # Чтение файлов в папке
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Создание JSON со структурой папки и контрольными суммами
    folder_structure = {}
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        checksum = calculate_checksum(file_path)
        folder_structure[file_name] = checksum

    json_data = json.dumps(folder_structure)
    serial_port.write(json_data.encode())

    # Отправка файлов
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        send_file(file_path, serial_port)
        time.sleep(port_settings['file_transfer_delay'])  # Задержка между передачей файлов

    logging.info(f"Содержимое папки {folder_path} успешно передано.")

def main():
    # Проверка наличия аргумента - имя папки для передачи
    if len(sys.argv) != 2:
        print("Использование: python sender_script.py <имя_папки>")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    folder_path = os.path.abspath(folder_name)

    # Загрузка настроек порта из файла
    with open('portsettings.json', 'r') as settings_file:
        port_settings = json.load(settings_file)

    # Установка соединения с COM портом
    serial_port = serial.Serial(port=port_settings['port'],
                                baudrate=port_settings['baudrate'],
                                parity=port_settings['parity'],
                                stopbits=port_settings['stopbits'],
                                bytesize=port_settings['bytesize'])

    # Передача содержимого папки
    send_folder(folder_path, serial_port, port_settings)

    # Закрытие порта
    serial_port.close()

if __name__ == "__main__":
    main()
