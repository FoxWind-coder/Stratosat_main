import os
import json
import time

def log(message, log_dir):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'[{timestamp}] {message}\n'
    log_file_path = os.path.join(log_dir, 'log.txt')
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_message)

def build_tree(path, log_dir):
    total_file_size = 0  # Суммарный размер файлов
    tree = {'name': os.path.basename(path), 'type': 'directory', 'children': []}
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_symlink():
                    log(f'Skipped symbolic link: {entry.path}', log_dir)
                    continue  # Пропускаем символические ссылки
                if entry.is_dir(follow_symlinks=False):
                    log(f'Reading directory: {entry.path}', log_dir)
                    subtree, subtree_size = build_tree(entry.path, log_dir)
                    tree['children'].append(subtree)
                    total_file_size += subtree_size
                else:
                    file_size = entry.stat().st_size / 1024  # Размер файла в килобайтах
                    total_file_size += file_size
                    log(f'Reading file: {entry.path} (size: {file_size:.2f} KB)', log_dir)
                    tree['children'].append({'name': entry.name, 'type': 'file', 'size_kb': file_size})
    except (PermissionError, OSError) as e:
        log(f'Error reading {path}: {e}', log_dir)
    return tree, total_file_size

def main(folder_path):
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    logs_dir = os.path.join(temp_dir, 'logs')

    # Ensure temp and logs directories exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log(f'Created directory: {temp_dir}', logs_dir)
    log(f'Created directory: {logs_dir}', logs_dir)

    log(f'Starting tree build for: {folder_path}', logs_dir)
    tree, total_size_kb = build_tree(folder_path, logs_dir)
    log(f'Finished tree build for: {folder_path}', logs_dir)

    output_path = os.path.join(temp_dir, 'tree.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree, f, ensure_ascii=False, indent=4)

    if total_size_kb > 2048:
        total_size_mb = total_size_kb / 1024
        log(f'JSON tree written to: {output_path} (size: {total_size_mb:.2f} MB)', logs_dir)
    else:
        log(f'JSON tree written to: {output_path} (size: {total_size_kb:.2f} KB)', logs_dir)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Построение JSON дерева директории')
    parser.add_argument('folder_path', help='Путь к папке, для которой нужно построить дерево')

    args = parser.parse_args()
    main(args.folder_path)
