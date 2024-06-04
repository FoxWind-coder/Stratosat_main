import tkinter as tk
from tkinter import filedialog, messagebox, Menu, Label, Entry, Checkbutton, IntVar, DoubleVar, Toplevel, Button, Text, Scrollbar, Frame, StringVar
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import os
import re
import random
import threading
from itertools import takewhile

class PixViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PIX Viewer")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.menu = Menu(self)
        self.config(menu=self.menu)

        file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        convert_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Convert", menu=convert_menu)
        convert_menu.add_command(label="To PIX", command=self.convert_to_pix)
        convert_menu.add_command(label="To JPG", command=self.convert_to_jpg)

        corrupt_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Corrupt", menu=corrupt_menu)
        corrupt_menu.add_command(label="Corrupt PIX File", command=self.open_corrupt_config)

        view_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Show", menu=view_menu)
        self.view_mode = StringVar(value="full")
        view_menu.add_radiobutton(label="Full", variable=self.view_mode, value="full", command=self.update_view_mode)
        view_menu.add_radiobutton(label="Fixed", variable=self.view_mode, value="fixed", command=self.update_view_mode)

        self.current_file_path = None
        self.image = None
        self.tk_image = None

        self.canvas.bind("<Configure>", self.resize_image)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<ButtonPress-3>", self.on_right_button_press)
        self.canvas.bind("<B3-Motion>", self.on_right_move_press)

        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_end_x = 0
        self.pan_end_y = 0
        self.scale_factor = 1.0

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PIX files", "*.pix"), ("JPG files", "*.jpg")])
        if file_path:
            self.current_file_path = file_path
            if file_path.endswith('.pix'):
                self.load_pix_file(file_path)
            elif file_path.endswith('.jpg'):
                self.load_jpg_file(file_path)
            else:
                self.show_error("Unsupported file format. Only PIX and JPG files can be displayed.")

    def load_pix_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Clean and restore the file if necessary
            restored_lines = self.restore_pix_file(lines)
            if restored_lines != lines:
                restored_file_path = os.path.join(os.path.dirname(file_path), f"restored_{os.path.basename(file_path)}")
                with open(restored_file_path, 'w') as restored_file:
                    restored_file.writelines(restored_lines)
                self.show_info(f"Restored file saved as {restored_file_path}")
                lines = restored_lines

            self.canvas.delete("all")
            self.image = self.create_image_from_pix(lines)
            self.scale_factor = 1.0
            self.display_image()

        except Exception as e:
            self.show_error(f"Failed to load file: {e}")

    def load_jpg_file(self, file_path):
        try:
            self.image = Image.open(file_path).convert('L')
            self.scale_factor = 1.0
            self.display_image()
        except Exception as e:
            self.show_error(f"Failed to load JPG file: {e}")

    def restore_pix_file(self, lines):
        cleaned_lines = [re.sub(r'[^0-9 ]', '', line) for line in lines]
        cleaned_lines = [re.sub(r'(\d)(?=\d)', r'\1 ', line) for line in cleaned_lines]
        max_length = max(len(re.findall(r'\d', line)) for line in cleaned_lines)

        restored_lines = []
        for line in cleaned_lines:
            numbers = line.split()
            if len(numbers) < max_length:
                numbers.extend(['0'] * (max_length - len(numbers)))
            elif len(numbers) > max_length:
                numbers = numbers[:max_length]
            restored_lines.append(' '.join(numbers) + "\n")

        return restored_lines

    def convert_to_pix(self):
        if not self.current_file_path or not self.current_file_path.endswith('.jpg'):
            self.show_error("No valid JPG file loaded for conversion.")
            return

        output_folder_path = filedialog.askdirectory()
        if output_folder_path:
            pix_file_path = self.convert_image_to_pix(self.current_file_path, output_folder_path)
            if pix_file_path:
                self.load_pix_file(pix_file_path)

    def convert_to_jpg(self):
        if not self.current_file_path or not self.current_file_path.endswith('.pix'):
            self.show_error("No valid PIX file loaded for conversion.")
            return

        output_folder_path = filedialog.askdirectory()
        if output_folder_path:
            self.convert_pix_to_image(self.current_file_path, output_folder_path)

    def convert_image_to_pix(self, input_image_path, output_folder_path):
        if not os.path.isfile(input_image_path):
            self.show_error(f"File {input_image_path} does not exist.")
            return None

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        img = Image.open(input_image_path).convert('L')
        width, height = img.size

        next_file_number = self.get_next_file_number(output_folder_path, "splash_", ".pix")
        output_file_path = os.path.join(output_folder_path, f"splash_{next_file_number}.pix")

        with open(output_file_path, 'w') as output_file:
            for y in range(height):
                line = []
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    gray_value = pixel // 26
                    line.append(str(gray_value))
                output_file.write(" ".join(line) + "\n")

        self.show_info(f"Image successfully converted to {output_file_path}")
        return output_file_path

    def convert_pix_to_image(self, input_pix_path, output_folder_path):
        if not os.path.isfile(input_pix_path):
            self.show_error(f"File {input_pix_path} does not exist.")
            return

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        next_file_number = self.get_next_file_number(output_folder_path, "converted_", ".jpg")
        output_image_path = os.path.join(output_folder_path, f"converted_{next_file_number}.jpg")

        try:
            img_data = self.load_pix_file_data(input_pix_path)
        except ValueError:
            with open(input_pix_path, 'r') as file:
                lines = file.readlines()
            restored_lines = self.restore_pix_file(lines)
            restored_file_path = os.path.join(os.path.dirname(input_pix_path), f"restored_{os.path.basename(input_pix_path)}")
            with open(restored_file_path, 'w') as restored_file:
                restored_file.writelines(restored_lines)
            img_data = self.load_pix_file_data(restored_file_path)
            self.show_info(f"Restored file saved as {restored_file_path}")

        img = self.create_image_from_data(img_data)
        img.save(output_image_path)

        self.show_info(f"Image successfully converted to {output_image_path}")

    def get_next_file_number(self, folder_path, prefix, suffix):
        max_number = 0
        pattern = re.compile(rf'{prefix}(\d+){suffix}')
        for filename in os.listdir(folder_path):
            match = pattern.match(filename)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number
        return max_number + 1

    def load_pix_file_data(self, input_pix_path):
        with open(input_pix_path, 'r') as f:
            lines = f.readlines()
            img_data = [[int(value) for value in line.strip().split()] for line in lines]
        return img_data

    def create_image_from_data(self, img_data):
        height = len(img_data)
        width = len(img_data[0])
        img = Image.new('L', (width, height))
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                gray_value = img_data[y][x] * 26
                pixels[x, y] = gray_value
        return img

    def create_image_from_pix(self, lines):
        img_data = [[int(value) for value in line.strip().split()] for line in lines]
        return self.create_image_from_data(img_data)

    def display_image(self):
        if self.image:
            mode = self.view_mode.get()
            if mode == "fixed":
                self.image = self.crop_image_if_needed(self.image)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def crop_image_if_needed(self, img):
        img_data = list(img.getdata())
        width, height = img.size
        img_data = [img_data[i * width:(i + 1) * width] for i in range(height)]

        def count_trailing_zeros(row):
            return len(list(takewhile(lambda x: x == 0, reversed(row))))

        cropped_height = height
        for y in range(height - 1, -1, -1):
            if count_trailing_zeros(img_data[y]) > width * 0.2:
                cropped_height = y
                break

        return img.crop((0, 0, width, cropped_height))

    def on_button_press(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_move_press(self, event):
        delta_x = event.x - self.pan_start_x
        delta_y = event.y - self.pan_start_y
        self.canvas.move(tk.ALL, delta_x, delta_y)
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_right_button_press(self, event):
        self.pan_end_x = event.x
        self.pan_end_y = event.y

    def on_right_move_press(self, event):
        delta_x = event.x - self.pan_end_x
        delta_y = event.y - self.pan_end_y
        self.canvas.move(tk.ALL, delta_x, delta_y)
        self.pan_end_x = event.x
        self.pan_end_y = event.y

    def on_mouse_wheel(self, event):
        scale = 1.0
        if event.delta > 0:
            scale = 1.1
        elif event.delta < 0:
            scale = 0.9

        self.scale_factor *= scale
        self.resize_image(event)

    def resize_image(self, event):
        if self.image:
            new_width = int(self.image.width * self.scale_factor)
            new_height = int(self.image.height * self.scale_factor)
            resized_image = self.image.resize((new_width, new_height), Image.NEAREST)
            self.tk_image = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def update_view_mode(self):
        self.display_image()

    def open_corrupt_config(self):
        if not self.current_file_path or not self.current_file_path.endswith('.pix'):
            file_path = filedialog.askopenfilename(filetypes=[("PIX files", "*.pix")])
            if not file_path:
                self.show_error("No valid PIX file selected for corruption.")
                return
            self.current_file_path = file_path

        output_folder_path = filedialog.askdirectory()
        if not output_folder_path:
            self.show_error("No valid output folder selected.")
            return

        config_window = Toplevel(self)
        config_window.title("Corrupt Configuration")

        Label(config_window, text="Damage Percentage:").grid(row=0, column=0)
        damage_percentage = DoubleVar(value=10)
        Entry(config_window, textvariable=damage_percentage).grid(row=0, column=1)

        Label(config_window, text="Damage Distance:").grid(row=1, column=0)
        damage_distance = IntVar(value=5)
        Entry(config_window, textvariable=damage_distance).grid(row=1, column=1)

        Label(config_window, text="Damage Rows Percentage:").grid(row=2, column=0)
        damage_rows_percentage = DoubleVar(value=10)
        Entry(config_window, textvariable=damage_rows_percentage).grid(row=2, column=1)

        shuffle_rows = IntVar(value=0)
        Checkbutton(config_window, text="Shuffle Rows", variable=shuffle_rows).grid(row=3, column=0, columnspan=2)

        Label(config_window, text="Shuffle Percentage:").grid(row=4, column=0)
        shuffle_percentage = DoubleVar(value=10)
        Entry(config_window, textvariable=shuffle_percentage).grid(row=4, column=1)

        log_frame = Frame(config_window)
        log_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        log_text = Text(log_frame, state="disabled", wrap="word")
        log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = Scrollbar(log_frame, command=log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_text.config(yscrollcommand=log_scroll.set)

        progress = Progressbar(config_window, mode="determinate")
        progress.grid(row=6, column=0, columnspan=2, sticky="ew")

        cancel_button = Button(config_window, text="Cancel", command=config_window.destroy)
        cancel_button.grid(row=7, column=0)

        corrupt_button = Button(config_window, text="Corrupt", command=lambda: self.start_corruption_thread(
            damage_percentage.get(),
            damage_distance.get(),
            damage_rows_percentage.get(),
            shuffle_rows.get(),
            shuffle_percentage.get(),
            output_folder_path,
            config_window,
            log_text,
            progress))
        corrupt_button.grid(row=7, column=1)

    def start_corruption_thread(self, damage_percentage, damage_distance, damage_rows_percentage, shuffle_rows, shuffle_percentage, output_folder_path, config_window, log_text, progress):
        corruption_thread = threading.Thread(target=self.corrupt_pix_file, args=(
            damage_percentage, damage_distance, damage_rows_percentage, shuffle_rows, shuffle_percentage, output_folder_path, config_window, log_text, progress))
        corruption_thread.start()

    def corrupt_pix_file(self, damage_percentage, damage_distance, damage_rows_percentage, shuffle_rows, shuffle_percentage, output_folder_path, config_window, log_text, progress):
        with open(self.current_file_path, 'r') as file:
            lines = file.readlines()

        corrupted_lines = self.corrupt_lines(lines, damage_percentage, damage_distance, damage_rows_percentage, shuffle_rows, shuffle_percentage, log_text, progress)
        output_file_path = os.path.join(output_folder_path, os.path.basename(self.current_file_path))

        with open(output_file_path, 'w') as file:
            file.writelines(corrupted_lines)

        self.show_info(f"File successfully corrupted and saved to {output_file_path}")
        config_window.destroy()

    def corrupt_lines(self, lines, damage_percentage, damage_distance, damage_rows_percentage, shuffle_rows, shuffle_percentage, log_text, progress):
        total_chars = sum(len(line) for line in lines)
        num_damages = int(total_chars * (damage_percentage / 100))
        damage_positions = random.sample(range(total_chars), num_damages)

        log_text.config(state="normal")
        log_text.insert("end", f"Total characters: {total_chars}\n")
        log_text.insert("end", f"Total damages: {num_damages}\n")
        log_text.config(state="disabled")

        progress["maximum"] = total_chars

        corrupted_lines = []
        current_pos = 0

        for line in lines:
            new_line = []
            for char in line:
                if current_pos in damage_positions:
                    if random.random() < 0.5:
                        new_char = random.choice(['@', '#', '$', '%', '&'])
                    else:
                        new_char = char
                    new_line.append(new_char)
                    damage_positions = [pos - 1 for pos in damage_positions]
                else:
                    new_line.append(char)
                current_pos += 1
                progress["value"] = current_pos
                progress.update()
            corrupted_lines.append(''.join(new_line))

        log_text.config(state="normal")
        log_text.insert("end", "Character corruption completed.\n")
        log_text.config(state="disabled")

        if shuffle_rows:
            num_rows = int(len(corrupted_lines) * (shuffle_percentage / 100))
            rows_to_shuffle = random.sample(range(len(corrupted_lines)), num_rows)
            log_text.config(state="normal")
            log_text.insert("end", f"Shuffling {num_rows} rows.\n")
            log_text.config(state="disabled")

            for i in range(len(rows_to_shuffle) // 2):
                idx1 = rows_to_shuffle[2 * i]
                idx2 = rows_to_shuffle[2 * i + 1]
                corrupted_lines[idx1], corrupted_lines[idx2] = corrupted_lines[idx2], corrupted_lines[idx1]

        log_text.config(state="normal")
        log_text.insert("end", "Row shuffling completed.\n")
        log_text.config(state="disabled")

        return corrupted_lines

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

if __name__ == "__main__":
    app = PixViewer()
    app.mainloop()
