import tkinter as tk
from tkinter import filedialog, messagebox, Menu
from PIL import Image
import os
import re

class PixViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PIX Viewer")
        self.geometry("1280x800")

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

        self.current_file_path = None

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PIX files", "*.pix"), ("JPG files", "*.jpg")])
        if file_path:
            self.current_file_path = file_path
            if file_path.endswith('.pix'):
                self.load_pix_file(file_path)
            else:
                self.show_error("Unsupported file format. Only PIX files can be displayed.")

    def load_pix_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Clean and restore the file if necessary
            lines = self.restore_pix_file(lines)

            self.canvas.delete("all")
            cell_size = 10
            for y, line in enumerate(lines):
                values = line.split()
                for x, value in enumerate(values):
                    gray_value = int(value) * 255 // 9  # Convert 0-9 to 0-255
                    color = f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
                    self.canvas.create_rectangle(x * cell_size, y * cell_size,
                                                 (x + 1) * cell_size, (y + 1) * cell_size,
                                                 outline=color, fill=color)
        except Exception as e:
            self.show_error(f"Failed to load file: {e}")

    def restore_pix_file(self, lines):
        # Step 1: Remove all characters except digits and spaces
        lines = [re.sub(r'[^0-9 ]', '', line) for line in lines]

        # Step 2: Add spaces where digits are consecutive
        lines = [re.sub(r'(\d)(?=\d)', r'\1 ', line) for line in lines]

        # Step 3: Find the longest line by the number of digits
        max_length = max(len(re.findall(r'\d', line)) for line in lines)

        # Step 4: Pad lines with zeros or trim them
        restored_lines = []
        for line in lines:
            numbers = line.split()
            if len(numbers) < max_length:
                numbers.extend(['0'] * (max_length - len(numbers)))
            elif len(numbers) > max_length:
                numbers = numbers[:max_length]
            restored_lines.append(' '.join(numbers))

        return restored_lines

    def convert_to_pix(self):
        if not self.current_file_path or not self.current_file_path.endswith('.jpg'):
            self.show_error("No valid JPG file loaded for conversion.")
            return

        output_folder_path = filedialog.askdirectory()
        if output_folder_path:
            self.convert_image_to_pix(self.current_file_path, output_folder_path)

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
            return

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

    def convert_pix_to_image(self, input_pix_path, output_folder_path):
        if not os.path.isfile(input_pix_path):
            self.show_error(f"File {input_pix_path} does not exist.")
            return

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        next_file_number = self.get_next_file_number(output_folder_path, "converted_", ".jpg")
        output_image_path = os.path.join(output_folder_path, f"converted_{next_file_number}.jpg")

        img_data = self.load_pix_file_data(input_pix_path)
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
                pixels[x, y] = int(img_data[y][x] * 25.5)  # Convert back from 0-9 range to 0-255 range
        return img

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

if __name__ == "__main__":
    app = PixViewer()
    app.mainloop()
