def parse_string(input_string):
    # Находим индексы начала и конца сегмента данных
    start_index = input_string.find("|||") + 3
    end_index = input_string.rfind("|||")
    
    # Выделяем сегмент данных
    data_segment = input_string[start_index:end_index]
    
    # Разделяем сегмент данных на части по разделителю "|"
    data_parts = data_segment.split("|")
    
    # Получаем команду
    command = data_parts[0]
    
    # Получаем аргументы
    arguments = data_parts[1:]
    
    # Запускаем функцию с данными аргументами
    try:
        getattr(__import__(__name__), command)(*arguments)
    except AttributeError:
        print("Функция '{}' не найдена".format(command))

# Пример использования
if __name__ == "__main__":
    input_string = "|||cmtf|arg1|arg2|arg3|||"
    parse_string(input_string)
