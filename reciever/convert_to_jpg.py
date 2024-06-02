#python3 back2pic.py /home/sky/capture/pointed/splash_1.pix /home/sky/capture/converted

import sys
import os
from PIL import Image

def main(input_pix_path, output_folder_path):
    # Check if the input file exists
    if not os.path.isfile(input_pix_path):
        print(f"File {input_pix_path} does not exist.")
        return

    # Check if the output folder exists, create if it doesn't
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Determine the next file number
    next_file_number = get_next_file_number(output_folder_path)

    # Path to the output file
    output_image_path = os.path.join(output_folder_path, f"converted_{next_file_number}.jpg")

    # Load pix file and convert to grayscale image
    img_data = load_pix_file(input_pix_path)
    img = create_image_from_data(img_data)

    # Save the image as jpg
    img.save(output_image_path)

    print(f"Image successfully saved to {output_image_path}")

def get_next_file_number(folder_path):
    max_number = 0
    for filename in os.listdir(folder_path):
        if filename.startswith("converted_") and filename.endswith(".jpg"):
            try:
                number = int(filename[10:-4])
                if number > max_number:
                    max_number = number
            except ValueError:
                continue
    return max_number + 1

def load_pix_file(input_pix_path):
    with open(input_pix_path, 'r') as f:
        lines = f.readlines()
        img_data = [[int(value) for value in line.strip().split()] for line in lines]
    return img_data

def create_image_from_data(img_data):
    height = len(img_data)
    width = len(img_data[0])
    img = Image.new('L', (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = int(img_data[y][x] * 25.5)  # Convert back from 0-9 range to 0-255 range
    return img

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <path to input .pix file> <path to output folder>")
    else:
        input_pix_path = sys.argv[1]
        output_folder_path = sys.argv[2]
        main(input_pix_path, output_folder_path)
