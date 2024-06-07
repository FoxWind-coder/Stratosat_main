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
    print("hello")

def test2(device_name):
    log(f"parsed: {device_name}", 'INFO')

def execute_capture_command(arg1, arg2, arg3, arg4, arg5, arg6):
    command = ["python3", "/home/sky/satcont_main/camera/capture/capture.py", arg1, arg2, arg3, arg4, arg5, arg6]
    log(f"Executing capture command: {' '.join(command)}", 'INFO')
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            log(f"[EXTERNAL] {result.stdout}", 'INFO')
        else:
            log(f"[EXTERNAL] {result.stderr}", 'ERROR')
    except Exception as e:
        log(f"[EXTERNAL] Error executing capture command: {e}", 'ERROR')

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
            else:
                log(f"not exist: {output_path}", 'WARNING')
        else:
            log(f"[EXTERNAL] {result.stderr}", 'ERROR')
    except Exception as e:
        log(f"[EXTERNAL] Error executing converting command: {e}", 'ERROR')

def manage_file(path, data, mode, operation, overwrite, hash_check, line_number=None):
    log(data, 'DEBUG')
    # Создание пути к файлу, если он не существует
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    
    # Проверка существования файла
    if not os.path.isfile(path):
        with open(path, 'w') as f:
            pass

    # Проверка хеша строки
    data_hash = hashlib.md5(data.encode()).hexdigest()[:3]
    if data_hash != hash_check:
        log("Hash mismatch: expected {}, got {}".format(hash_check, data_hash), 'WARNING')
        return "Warning: Hash mismatch"

    # Чтение текущего содержимого файла
    with open(path, 'r') as file:
        lines = file.readlines()

    # Выполнение операций над содержимым файла
    if operation == 'nstring':
        if overwrite:
            with open(path, 'w') as file:
                file.write(data + '\n')
        else:
            with open(path, 'a') as file:
                file.write(data + '\n')
    elif operation == 'sstring':
        if line_number is not None:
            line_number = int(line_number) - 1
            if line_number < len(lines):
                lines[line_number] = lines[line_number].strip() + data + '\n'
            else:
                lines.append(data + '\n')
        else:
            lines.append(data + '\n')
        
        with open(path, 'w') as file:
            file.writelines(lines)
    elif operation == 'rstring':
        if line_number is not None:
            line_number = int(line_number) - 1
            if line_number < len(lines):
                lines[line_number] = data + '\n'
            else:
                lines.append(data + '\n')
        
        with open(path, 'w') as file:
            file.writelines(lines)
    
    log_message = f"Data written to {path} with operation {operation}"
    if verbose_logging:
        log(log_message, 'DEBUG')
    else:
        log(log_message, 'INFO')
    return "Data written successfully"

def file_command(path, data, operation, overwrite, hash_check, line_number=None):
    result = manage_file(path, data, operation, overwrite, hash_check, line_number)
    log(result, 'INFO')
    return result

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

    uart.add_command(1, test1, release_port_during_execution=True)
    uart.add_command(2, test2, release_port_during_execution=False)
    uart.add_command(3, execute_capture_command, release_port_during_execution=False)
    uart.add_command(4, pic2point, release_port_during_execution=False)
    uart.add_command(5, file_command, release_port_during_execution=False)

    # parallel uart listening
    listener_thread = threading.Thread(target=uart.listen)
    listener_thread.start()
    
    log("UART listener started.", 'INFO')

# Example usage:
# python3 main.py --port 2 --baudrate 115200
# ++3+/home/sky/capture:str+640:str+320:str+4:str+black:str+10:str++
# ++4+/home/sky/capture/capture_3.jpg:str+/home/sky/capture/pointed:str++
# ++5+/home/sky/aaaaaaaaaaaa/file.txt:str+Some data:str+rstring:str+False:bool+0:str+5b8:str++
