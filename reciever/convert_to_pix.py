#python3 pointillism.py /home/sky/capture/capture_1.jpg /home/sky/capture/pointed

import sys
import os
from PIL import Image

def get_next_file_number(folder_path):
    max_number = 0
    for filename in os.listdir(folder_path):
        if filename.startswith("splash_") and filename.endswith(".pix"):
            try:
                number = int(filename[7:-4])
                if number > max_number:
                    max_number = number
            except ValueError:
                continue
    return max_number + 1

def main(input_image_path, output_folder_path):
    # Check if the input file exists
    if not os.path.isfile(input_image_path):
        print(f"File {input_image_path} does not exist.")
        return

    # Check if the output folder exists, create if it doesn't
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Open the image and convert it to grayscale
    img = Image.open(input_image_path).convert('L')
    width, height = img.size

    # Determine the next file number
    next_file_number = get_next_file_number(output_folder_path)

    # Path to the output file
    output_file_path = os.path.join(output_folder_path, f"splash_{next_file_number}.pix")

    with open(output_file_path, 'w') as output_file:
        for y in range(height):
            line = []
            for x in range(width):
                pixel = img.getpixel((x, y))
                # Convert pixel value from 0-255 to 0-9
                gray_value = pixel // 26  # 26 = 256 / 10, to get values from 0 to 9
                line.append(str(gray_value))
            output_file.write(" ".join(line) + "\n")

    print(f"{output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <path to input image> <path to output folder>")
    else:
        input_image_path = sys.argv[1]
        output_folder_path = sys.argv[2]
        main(input_image_path, output_folder_path)
