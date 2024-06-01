import serial
import threading
import platform
import time
import multiprocessing
import datetime
import os

# verbose
verbose_logging = True

def log(message, level='INFO'):
    if not os.path.exists('logs'):   # mkdir
        os.makedirs('logs')
    log_file = os.path.join('logs', datetime.datetime.now().strftime('%Y-%m-%d') + '.log') # filename forming "YYYY-MM-DD.log"
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # adding timestamp
    log_message = f'[{timestamp}] [{level}] {message}'
    with open(log_file, 'a') as f:  # write log
        f.write(log_message + '\n')
    print(log_message) # print log

def get_full_port_name(port):
    os_type = platform.system()
    if os_type == "Windows":
        return f"COM{port}"
    elif os_type == "Linux":
        return f"/dev/ttyS{port}"
    else:
        raise ValueError("Unsupported OS")

class UARTCommand:
    def __init__(self, port, baudrate):
        full_port_name = get_full_port_name(port)
        self.ser = serial.Serial(full_port_name, baudrate)
        self.commands = {}
        log("UART initialized with port: {} and baudrate: {}".format(full_port_name, baudrate), 'DEBUG')

    def add_command(self, command_number, function, release_port_during_execution=False):
        self.commands[command_number] = {
            "function": function,
            "release_port_during_execution": release_port_during_execution
        }
        log("Added command number: {} with function: {} and release_port_during_execution: {}".format(
            command_number, function.__name__, release_port_during_execution), 'DEBUG')

    def parse_command(self, command):
        log("Parsing command: {}".format(command), 'DEBUG')
        if verbose_logging:
            log("Received command from UART: {}".format(command), 'DEBUG')

        command = command.strip()
        if not command:
            log("Empty command received, ignoring", 'WARNING')
            return None, None

        parts = command.strip("++").split('+')
        command_number = int(parts[0])
        args = parts[1:]
        parsed_args = []

        for arg in args:
            if ':' not in arg:
                raise ValueError("Invalid argument format, missing type specifier")
            value, type_specifier = arg.split(':')
            if type_specifier == 'str':
                parsed_args.append(value)
            elif type_specifier == 'int':
                parsed_args.append(int(value))
            else:
                raise ValueError("Unsupported type specifier")
        log("Parsed command number: {} with arguments: {}".format(command_number, parsed_args), 'DEBUG')
        return command_number, parsed_args

    def execute_command(self, command):
        try:
            log("Executing command: {}".format(command), 'DEBUG')
            command_number, args = self.parse_command(command)
            if command_number in self.commands:
                self.commands[command_number]["function"](*args)
                log("Command executed successfully: {}".format(command_number), 'INFO')
            else:
                self.send_error("Unknown command")
        except Exception as e:
            log("Error during command execution: {}".format(e), 'ERROR')
            self.send_error(str(e))

    def send_error(self, message):
        log("Sending error message: {}".format(message), 'ERROR')
        self.ser.write(f"Error: {message}\n".encode())

    def listen(self):
        log("Listening for incoming commands", 'INFO')
        current_command = ""
        while True:
            command_start_time = time.time()
            command_timeout = 10  # timeout
            timeout_occurred = False
            while time.time() - command_start_time < command_timeout:
                try:
                    char = self.ser.read().decode()
                    if char:
                        if char == '+':
                            if current_command and current_command[-1] == '+':
                                self.execute_command(current_command)
                                current_command = ""
                                break 
                            else:
                                current_command += char
                        else:
                            current_command += char
                except serial.SerialTimeoutException:
                    log("Timeout occurred while waiting for data", 'WARNING')
                    timeout_occurred = True
                    break 
            if time.time() - command_start_time >= command_timeout:
                log("Command timeout occurred", 'WARNING')
                timeout_occurred = True
            if timeout_occurred:
                current_command = ""  # clear
