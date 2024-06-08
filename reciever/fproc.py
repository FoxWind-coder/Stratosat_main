import argparse
import hashlib
import os
import platform

def generate_command(path, data, mode, line_number):
    # Вычисление хеша данных
    data_hash = hashlib.md5(data.encode()).hexdigest()[:3]
    # Форматирование команды
    command = f"++5+{path}:str+{data}:str+{mode}:str+{data_hash}:str+{line_number}:int++"
    return command

def process_file(file_path, additional_path, algorithm, os_type, max_chars=None):
    with open(file_path, 'r') as file:
        content = file.read()
    
    commands = []
    
    if os_type == 'windows':
        relative_path = os.path.join(additional_path, os.path.relpath(file_path, start=os.getcwd())).replace('/', '\\')
    else:
        relative_path = os.path.join(additional_path, os.path.relpath(file_path, start=os.getcwd())).replace('\\', '/')
    
    if algorithm == 'upstring':
        lines = content.splitlines()
        for i, line in enumerate(lines, start=1):
            command = generate_command(relative_path, line, 'nstring', i)
            commands.append(command)
    else:
        chunk_size = int(algorithm)
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            line_number = (i // chunk_size) + 1
            command = generate_command(relative_path, chunk, 'nstring', line_number)
            commands.append(command)
    
    return commands

def process_directory(directory_path, additional_path, algorithm, os_type, max_chars=None):
    commands = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            commands.extend(process_file(file_path, additional_path, algorithm, os_type, max_chars))
    return commands

def save_commands(commands, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    existing_files = [f for f in os.listdir(output_dir) if f.startswith('upload_') and f.endswith('.upld')]
    next_number = len(existing_files) + 1
    output_file = os.path.join(output_dir, f'upload_{next_number}.upld')

    with open(output_file, 'w') as f:
        for command in commands:
            f.write(command + '\n')
    
    print(f"Commands saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate commands for files in a directory")
    parser.add_argument('path', type=str, help="Path to the directory or file to process")
    parser.add_argument('additional_path', type=str, help="Additional path to prepend to file paths in commands")
    parser.add_argument('algorithm', type=str, help="Algorithm to use: 'upstring' or a number for chunk size")
    parser.add_argument('os_type', type=str, help="Operating system type: 'windows' or 'linux'")
    
    args = parser.parse_args()

    if os.path.isdir(args.path):
        commands = process_directory(args.path, args.additional_path, args.algorithm, args.os_type)
    elif os.path.isfile(args.path):
        commands = process_file(args.path, args.additional_path, args.algorithm, args.os_type)
    else:
        print("Invalid path specified")
        return
    
    save_commands(commands, os.path.join(os.path.dirname(__file__), 'upload'))

if __name__ == "__main__":
    main()
