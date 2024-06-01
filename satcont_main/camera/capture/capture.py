#python3 capture.py /home/sky/capture 1280 720 4 black 10

#python3 capture.py /home/sky/capture 1280 720 4 color 16


import cv2
import sys
import os

def capture_image(output_folder, resolution, camera_index, mode, depth):
    # Open the camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Unable to open camera.")
        return

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame.")
        return

    # Convert to grayscale if mode is black
    if mode == "black":
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert to specified number of gray shades
        gray_frame = (gray_frame / (256 / depth)).astype('uint8') * (256 / depth)
        output_file = "capture_" + str(len(os.listdir(output_folder))) + ".jpg"
    elif mode == "color":
        # Convert to specified color depth
        output_file = "capture_" + str(len(os.listdir(output_folder))) + "_color_depth_" + str(depth) + ".jpg"
        frame = (frame / (256 / depth)).astype('uint8') * (256 / depth)
        gray_frame = frame
    else:
        print("Error: Invalid mode specified.")
        return

    # Save the image
    cv2.imwrite(os.path.join(output_folder, output_file), gray_frame)

    print("{}".format(os.path.join(output_folder, output_file)))

    # Release the camera
    cap.release()

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python script.py <output_folder> <width> <height> <camera_index> <mode> <depth>")
        sys.exit(1)

    output_folder = sys.argv[1]
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    camera_index = int(sys.argv[4])
    mode = sys.argv[5]
    depth = int(sys.argv[6])
    resolution = (width, height)

    if not os.path.exists(output_folder):
        print("Error: Output folder does not exist.")
        sys.exit(1)

    if mode not in ["color", "black"]:
        print("Error: Invalid mode specified.")
        sys.exit(1)

    capture_image(output_folder, resolution, camera_index, mode, depth)
