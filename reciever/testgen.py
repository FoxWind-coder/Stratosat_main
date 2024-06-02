import sys
import random

def generate_test_file(num_lines, line_length, output_path):
    with open(output_path, 'w') as file:
        for _ in range(num_lines):
            # Генерируем строку случайных цифр
            line = ''.join(str(random.randint(0, 9)) for _ in range(line_length))
            
            # Добавляем "шум" в строку, например, символы
            noise = ''.join(random.choice(['', ' ', 'a', 'b', '@', '#', '\n']) for _ in range(random.randint(0, 5)))
            line = noise + line + noise
            
            # Записываем строку в файл
            file.write(line + '\n')

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_test_file.py <num_lines> <line_length> <output_path>")
        return

    num_lines = int(sys.argv[1])
    line_length = int(sys.argv[2])
    output_path = sys.argv[3]

    generate_test_file(num_lines, line_length, output_path)

if __name__ == "__main__":
    main()
