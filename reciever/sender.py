import serial
import time
import sys
import os
import platform

def get_serial_port_name(port_number):
    system_name = platform.system()
    if system_name == 'Windows':
        return f'COM{port_number}'
    else:
        return f'/dev/ttyS{port_number}'

def send_data(port, baudrate, chunk_size, delay, file_path):
    port_name = get_serial_port_name(port)
    ser = serial.Serial()
    ser.baudrate = baudrate
    ser.port = port_name
    
    try:
        ser.open()
    except serial.SerialException as e:
        print(f"Не удалось открыть порт {port_name}: {e}")
        return

    try:
        # Читаем файл построчно
        with open(file_path, 'r') as file:
            for line in file:
                # Разделяем строку на фрагменты
                for i in range(0, len(line), chunk_size):
                    chunk = line[i:i+chunk_size]
                    # Отправляем фрагмент
                    ser.write(chunk.encode())
                    # Ожидаем заданное время
                    time.sleep(delay / 1000.0)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python script.py <port> <baudrate> <chunk_size> <delay> <file_path>")
        sys.exit(1)

    port = int(sys.argv[1])
    baudrate = int(sys.argv[2])
    chunk_size = int(sys.argv[3])
    delay = int(sys.argv[4])
    file_path = sys.argv[5]

    if not os.path.isfile(file_path):
        print(f"Файл {file_path} не найден")
        sys.exit(1)

    send_data(port, baudrate, chunk_size, delay, file_path)
