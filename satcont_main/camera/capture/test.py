import tkinter as tk
from tkinter import ttk
import subprocess
import time
import os
from PIL import Image

# Глобальная переменная для хранения пути к последнему захваченному изображению
last_captured_image = ""

def capture_image():
    global last_captured_image
    
    output_folder = "/home/sky/capture"
    resolution = (1280, 720)
    camera_index = 4
    mode = "black"
    depth = 10

    # Очистка текстового поля перед выполнением нового захвата
    log_text.delete(1.0, tk.END)

    # Выполнение скрипта capture.py
    result = subprocess.run(["python3", "capture.py", output_folder, str(resolution[0]), str(resolution[1]), str(camera_index), mode, str(depth)], capture_output=True, text=True)

    # Получение имени файла из вывода скрипта
    image_file = result.stdout.strip()
    
    # Сохранение пути к захваченному изображению в глобальную переменную
    last_captured_image = image_file

    # Добавление вывода в лог
    log_text.insert(tk.END, result.stdout)

    # Подписка на обновление изображения
    update_image(image_file)

def convert_image():
    global last_captured_image
    
    # Проверка, было ли захвачено изображение
    if not last_captured_image:
        # Если изображение еще не захвачено, выполняем захват
        capture_image()

    # Вызов скрипта pointillism.py с передачей пути к изображению и пути сохранения конвертированного файла
    result = subprocess.run(["python3", "pointillism.py", last_captured_image, "/home/sky/capture/pointed"], capture_output=True, text=True)
    log_text.insert(tk.END, result.stdout)

def update_image(image_path):
    # Отображение сохраненного изображения
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            raise FileNotFoundError("Error: File not found")

        # Проверяем, является ли файл изображением JPEG
        if not image_path.endswith('.jpg'):
            raise ValueError("Error: File is not a JPEG image")

        # Пауза для убедительности, что файл доступен для чтения
        time.sleep(0.1)

        # Конвертируем изображение из JPEG в PNG
        img_jpg = Image.open(image_path)

        # Проверяем, есть ли у изображения альфа-канал
        if len(img_jpg.split()) == 4:
            img_png = Image.new("RGB", img_jpg.size, (255, 255, 255))
            img_png.paste(img_jpg, mask=img_jpg.split()[3])  # используем маску альфа-канала
        else:
            img_png = img_jpg.convert('RGB')  # преобразуем изображение без альфа-канала

        # Изменяем размер изображения
        img_png.thumbnail((240, 240))

        img_png_path = "/tmp/temp_image.png"  # временный путь для сохранения сконвертированного изображения

        # Сохраняем сконвертированное изображение в формате PNG
        img_png.save(img_png_path)

        # Открываем сконвертированное изображение с помощью PIL
        img = tk.PhotoImage(file=img_png_path)

        # Проверка, если изображение уже отображается, удалите его
        for widget in right_frame.winfo_children():
            widget.destroy()

        # Создаем метку для отображения изображения
        label = tk.Label(right_frame, image=img)
        label.image = img  # сохраняем ссылку на объект PhotoImage, чтобы избежать его удаления
        label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)  # Отображение в правом нижнем углу с отступами
    except (FileNotFoundError, ValueError) as e:
        print(e)

root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg='white')

# Создание кнопки Capture
capture_button = ttk.Button(root, text="Capture", command=capture_image)
capture_button.place(x=10, y=10)

# Создание кнопки Convert
convert_button = ttk.Button(root, text="Convert", command=convert_image)
convert_button.place(x=10, y=40)

# Создание рамки для текстового поля лога
log_frame = tk.Frame(root, bg='white')
log_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1, anchor=tk.NW)

# Создание текстового поля для вывода лога
log_text = tk.Text(log_frame, bg='white', wrap='word')
log_text.pack(expand=True, fill='both')

# Создание правой рамки для отображения изображения
right_frame = tk.Frame(root, bg='white')
right_frame.place(relx=1.0, rely=1.0, anchor=tk.SE)  # закрепление в правом нижнем углу

root.mainloop()
