import os
import time
import cv2

ENROLLMENT_FOLDER = "enrollment_images"
CAPTURE_COUNT = 1
ENROLL_IMG_FORMAT = ".png"

#enrollement

def create_enrollment_folder(student_name):
    path = os.path.join(ENROLLMENT_FOLDER, student_name)
    os.makedirs(path, exist_ok=True)
    return path

def save_enrollment_image(student_name, frame, image_index):
    folder = create_enrollment_folder(student_name)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    img_name = f"{student_name}_{timestamp}_{image_index + 1}{ENROLL_IMG_FORMAT}"
    img_path = os.path.join(folder, img_name)
    success = cv2.imwrite(img_path, frame)
    return success, img_path
