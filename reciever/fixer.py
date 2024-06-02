import sys
import os
import json
import re

def read_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data.get('width'), data.get('height')

def process_file(input_path, output_path, max_length=None):
    with open(input_path, 'r') as file:
        lines = file.readlines()

    cleaned_lines = []
    max_num_count = 0

    for line in lines:
        # Убираем все, кроме чисел и пробелов
        cleaned_line = ''.join(char for char in line if char.isdigit() or char.isspace())

        # Добавляем пробелы между подряд идущими цифрами
        cleaned_line = re.sub(r'(\d)(?=\d)', r'\1 ', cleaned_line)

        # Считаем количество чисел в строке
        num_count = len(cleaned_line.split())
        if num_count > max_num_count:
            max_num_count = num_count

        cleaned_lines.append(cleaned_line)

    # Если max_length не задан, берем максимальное количество чисел из строк
    max_length = max_length if max_length else max_num_count

    processed_lines = []
    for line in cleaned_lines:
        num_count = len(line.split())

        # Заполняем строку нулями до необходимой длины или обрезаем ее
        if num_count < max_length:
            line = line.strip() + ' ' + '0 ' * (max_length - num_count)
        elif num_count > max_length:
            line = ' '.join(line.split()[:max_length])
        
        processed_lines.append(line.strip())

    with open(output_path, 'w') as file:
        for line in processed_lines:
            file.write(line + '\n')

def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    json_path = sys.argv[3] if len(sys.argv) > 3 else None

    if json_path:
        max_length, _ = read_json(json_path)
    else:
        max_length = None

    process_file(input_path, output_path, max_length)

if __name__ == "__main__":
    main()
