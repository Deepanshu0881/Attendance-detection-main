import csv
import os
from datetime import datetime
from PIL import Image, ImageOps
import cv2
import numpy as np
import face_recognition

ENROLLMENT_FOLDER = "enrollment_images"
ATTENDANCE_LOG_FOLDER = "attendance_logs"
TOLERANCE = 0.55
MODEL = "hog"

def save_failed_face(image, location, prefix="fail"):
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H%M%S")

    fail_dir = os.path.join("failures", today)
    os.makedirs(fail_dir, exist_ok=True)

    top, right, bottom, left = location
    face_crop = image[top:bottom, left:right]

    filename = f"{prefix}_{time_str}_{np.random.randint(1000)}.jpg"
    filepath = os.path.join(fail_dir, filename)
    cv2.imwrite(filepath, cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR))

    # Log to CSV
    log_path = os.path.join(fail_dir, f"failures_log_{today}.csv")
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if os.path.getsize(log_path) == 0:
            writer.writerow(["Filename", "Timestamp", "Reason"])
        writer.writerow([filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Unknown Face"])

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(ENROLLMENT_FOLDER):
        return known_face_encodings, known_face_names

    for person_name in os.listdir(ENROLLMENT_FOLDER):
        person_dir = os.path.join(ENROLLMENT_FOLDER, person_name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        path = os.path.join(person_dir, filename)
                        with Image.open(path) as img:
                            img.verify()

                        with Image.open(path) as img:
                            img = img.convert("RGB")
                            if max(img.size) > 1000:
                                img = ImageOps.contain(img, (800, 800))

                            image = np.asarray(img)
                            if image.ndim != 3 or image.shape[2] != 3:
                                raise ValueError(f"Invalid image shape: {image.shape}")
                            if image.dtype != np.uint8:
                                image = (image * 255).astype(np.uint8)

                        locations = face_recognition.face_locations(image, model=MODEL)
                        if not locations:
                            raise ValueError(f"No face found in image {filename}")

                        encodings = face_recognition.face_encodings(image, known_face_locations=locations)
                        if encodings:
                            known_face_encodings.append(encodings[0])
                            known_face_names.append(person_name)

                    except Exception as e:
                        print(f"❌ Error loading {filename} for {person_name}: {e}")

    return known_face_encodings, known_face_names

def get_today_log_filename():
    if not os.path.exists(ATTENDANCE_LOG_FOLDER):
        os.makedirs(ATTENDANCE_LOG_FOLDER)
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(ATTENDANCE_LOG_FOLDER, f"attendance_{today}.csv")

def mark_attendance(name):
    filename = get_today_log_filename()
    already_present = set()

    if os.path.exists(filename):
        with open(filename, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row:
                    already_present.add(row[0])

    if name in already_present:
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if os.path.getsize(filename) == 0:
            writer.writerow(['Name', 'Timestamp'])
        writer.writerow([name, timestamp])
    return True

def mark_attendance_from_image(image_np, known_encodings, known_names):
    marked_names = set()
    face_locations = face_recognition.face_locations(image_np, model=MODEL)
    face_encodings = face_recognition.face_encodings(image_np, face_locations)

    for (location, face_encoding) in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
        dist = face_recognition.face_distance(known_encodings, face_encoding)
        if len(dist) > 0:
            best = np.argmin(dist)
            if matches[best]:
                name = known_names[best]
                if name not in marked_names and mark_attendance(name):
                    marked_names.add(name)
            else:
                save_failed_face(image_np, location, prefix="photo")
        else:
            save_failed_face(image_np, location, prefix="photo")
    return list(marked_names)

def mark_attendance_from_video(video_path, known_encodings, known_names, frame_interval=30):
    marked_names = set()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video.")
        return list(marked_names)

    frame_id = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_interval == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model=MODEL)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (location, face_encoding) in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=TOLERANCE)
                dist = face_recognition.face_distance(known_encodings, face_encoding)
                if len(dist) > 0:
                    best = np.argmin(dist)
                    if matches[best]:
                        name = known_names[best]
                        if name not in marked_names and mark_attendance(name):
                            marked_names.add(name)
                    else:
                        save_failed_face(rgb_frame, location, prefix="video")
                else:
                    save_failed_face(rgb_frame, location, prefix="video")

        frame_id += 1

    cap.release()
    return list(marked_names)
