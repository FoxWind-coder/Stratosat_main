import hashlib

def get_input(prompt):
    return input(prompt).strip()

def generate_command(path, data, mode, hash_check, line_number):
    # Форматирование команды
    command = f"++5+{path}:str+{data}:str+{mode}:str+{hash_check}:str+{line_number}:int++"
    return command

def main():
    print("Введите параметры для функции manage_file:")
    
    # Получение данных от пользователя
    path = get_input("Введите путь к файлу: ")
    data = get_input("Введите данные для записи: ")
    mode = get_input("Введите режим работы (rstring, nstring, sstring, replace, remove): ")
    
    # Генерация хеша данных
    data_hash = hashlib.md5(data.encode()).hexdigest()[:3]
    
    if mode != 'remove':
        line_number = int(get_input("Введите номер строки (0 для конца файла, -1 для начала файла): "))
    else:
        line_number = 0  # Для режима remove номер строки не важен
    
    # Генерация команды
    command = generate_command(path, data, mode, data_hash, line_number)
    
    print(f"Сформированная команда: {command}")

if __name__ == "__main__":
    main()
