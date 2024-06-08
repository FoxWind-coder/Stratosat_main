import argparse
import threading
from uart_command import UARTCommand, log, verbose_logging, get_full_port_name
import serial
import os
import json
import subprocess
import hashlib

def test1(arg1, arg2, arg3):
    log(f"parsed arguments: {arg1} {arg2} {arg3}", 'INFO')
    return "hello"

def test2(device_name):
    log(f"parsed: {device_name}", 'INFO')
    return f"device_name: {device_name}"

def execute_capture_command(arg1, arg2, arg3, arg4, arg5, arg6):
    command = ["python3", "/home/sky/satcont_main/camera/capture/capture.py", arg1, arg2, arg3, arg4, arg5, arg6]
    log(f"Executing capture command: {' '.join(command)}", 'INFO')
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            log(f"[EXTERNAL] {result.stdout}", 'INFO')
            return result.stdout.strip()
        else:
            log(f"[EXTERNAL] {result.stderr}", 'ERROR')
            return result.stderr.strip()
    except Exception as e:
        log(f"[EXTERNAL] Error executing capture command: {e}", 'ERROR')
        return str(e)

def pic2point(source, save):
    command = ["python3", "/home/sky/satcont_main/camera/capture/pointillism.py", source, save]
    log(f"Executing converting: {' '.join(command)}", 'INFO')
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output_path = result.stdout.strip()
            log(f"[EXTERNAL] {output_path}", 'INFO')
            if os.path.exists(output_path):
                data = {"converted_file": output_path}
                json_file_path = "/home/sky/capture/pointed/ptconv.json"
                os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
                with open(json_file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                log(f"Path {output_path} written to {json_file_path}", 'INFO')
                return json_file_path
            else:
                log(f"not exist: {output_path}", 'WARNING')
                return "Output path does not exist"
        else:
            log(f"[EXTERNAL] {result.stderr}", 'ERROR')
            return result.stderr.strip()
    except Exception as e:
        log(f"[EXTERNAL] Error executing converting command: {e}", 'ERROR')
        return str(e)

def manage_file(path, data, mode, hash_check, line_number=0):
    log(f"Managing file: {path}", 'INFO')

    # Создание пути к файлу, если он не существует
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
        log(f"Created directory for path: {path}", 'INFO')

    # Проверка хеша строки
    data_hash = hashlib.md5(data.encode()).hexdigest()[:3]
    if data_hash != hash_check:
        log(f"Hash mismatch for data: {data}", 'WARNING')
        return "Hash mismatch warning"

    # Удаление файла, если mode == 'remove'
    if mode == 'remove':
        if os.path.exists(path):
            os.remove(path)
            log(f"Removed file: {path}", 'INFO')
        else:
            log(f"File does not exist: {path}", 'WARNING')
        return "File removed"

    # Проверка существования файла
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass
        log(f"Created empty file: {path}", 'INFO')

    # Чтение текущего содержимого файла
    with open(path, 'r') as f:
        lines = f.readlines()
    
    log(f"Read {len(lines)} lines from file: {path}", 'INFO')

    # Выполнение операций над содержимым файла
    if mode == 'nstring':
        if line_number == 0:
            lines.append(data + '\n')
        elif line_number == -1:
            lines.insert(0, data + '\n')
        elif 1 <= line_number <= len(lines):
            lines.insert(line_number, data + '\n')
        else:
            lines.append(data + '\n')
        log(f"Added new string to file: {path}", 'INFO')

    elif mode == 'sstring':
        if line_number == 0:
            if lines:
                lines[-1] = lines[-1].rstrip('\n') + data + '\n'
            else:
                lines.append(data + '\n')
        elif line_number == -1:
            if lines:
                lines[0] = lines[0].rstrip('\n') + data + '\n'
            else:
                lines.append(data + '\n')
        elif 1 <= line_number <= len(lines):
            lines[line_number - 1] = lines[line_number - 1].rstrip('\n') + data + '\n'
        else:
            lines.append(data + '\n')
        log(f"Appended data to line {line_number} in file: {path}", 'INFO')

    elif mode == 'rstring':
        if 1 <= line_number <= len(lines):
            lines[line_number - 1] = data + '\n'
        else:
            lines.append(data + '\n')
        log(f"Replaced data in line {line_number} in file: {path}", 'INFO')

    elif mode == 'replace':
        lines = [data + '\n']
        log(f"Replaced all content in file: {path}", 'INFO')

    else:
        log(f"Unsupported mode: {mode}", 'ERROR')
        return "Unsupported mode"

    # Запись изменений в файл
    with open(path, 'w') as f:
        f.writelines(lines)

    log(f"Operation {mode} performed on file {path}", 'INFO')
    return "success"

if __name__ == "__main__":
    # arg parser
    parser = argparse.ArgumentParser(description="UART Command Execution")
    parser.add_argument('--verbose', action='store_true', help="Enable detailed logging")
    parser.add_argument('--port', type=int, required=True, help="UART port number")
    parser.add_argument('--baudrate', type=int, required=True, help="UART baud rate")
    args = parser.parse_args()

    # use --verbose to activate verbose logging
    verbose_logging = args.verbose

    # got port name
    full_port_name = get_full_port_name(args.port)
    
    # port init
    ser = serial.Serial(full_port_name, args.baudrate)

    #  starting marker
    ser.write("started\n".encode())

    # port setup (number and baudrate)
    uart = UARTCommand(port=args.port, baudrate=args.baudrate)
    
    # Commands: command number
    # add_command takes the command number (used to check for arguments), 
    # the name of the executable function, and the need to release the port for function execution.
    # The command is called using the following format:
    # ++command_number+arg1:type+arg2:type+arg3:type
    # Example:
    # ++1+FoxWind:str+1234:int+example:str++
    # You can change the verbose logging value to True inside uart_command.py if you need to debug the code.
    # Note: that the error log processing and output for parsing and command processing are provided, although they are not perfect.
    # ++5+/home/sky/test123.txt:str+12345ahahahaha:str+remove:str+d21:str+3:int++

    uart.add_command(1, test1, release_port_during_execution=True)
    uart.add_command(2, test2, release_port_during_execution=False)
    uart.add_command(3, execute_capture_command, release_port_during_execution=False)
    uart.add_command(4, pic2point, release_port_during_execution=False)
    uart.add_command(5, manage_file, release_port_during_execution=False)
    # parallel uart listening
    listener_thread = threading.Thread(target=uart.listen)
    listener_thread.start()
    
    log("UART listener started.", 'INFO')
