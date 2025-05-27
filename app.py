import os
import streamlit as st
import cv2
import time
import numpy as np
import face_recognition
from PIL import Image
from enroll import save_enrollment_image, create_enrollment_folder
from attendance import load_known_faces, mark_attendance, mark_attendance_from_image, mark_attendance_from_video

CAPTURE_COUNT = 1
RESIZE_FACTOR = 0.25
MODEL = "hog"
TOLERANCE = 0.55

st.set_page_config(page_title="Face Attendance System", layout="wide")
st.title("📸 Face Recognition Attendance System")

page = st.sidebar.radio("Select Page", ["Enroll", "Mark Attendance"])

if page == "Enroll":
    st.header("👤 Enroll New Student")
    name = st.text_input("Enter Student Name")

    method = st.radio("Select Enrollment Method", ["Use Webcam", "Upload Photo"])

    if name:
        if method == "Use Webcam":
            cap = cv2.VideoCapture(0)
            stframe = st.empty()
            count = 0

            capture_btn = st.button("📸 Capture Image", key="capture_button")
            stop_btn = st.button("❌ Stop Camera", key="stop_enroll")

            if cap.isOpened():
                while cap.isOpened() and count < CAPTURE_COUNT:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Camera error.")
                        break

                    stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

                    if capture_btn:
                        success, path = save_enrollment_image(name, frame, count)
                        if success:
                            count += 1
                            st.success(f"Image {count} saved: {path}")
                        else:
                            st.error("Failed to save image.")

                    if stop_btn:
                        break

                cap.release()
                cv2.destroyAllWindows()

                if count == CAPTURE_COUNT:
                    st.success("✅ Enrollment Complete!")

        elif method == "Upload Photo":
            uploaded_file = st.file_uploader("Upload a clear image of the student", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert('RGB')
                st.image(image, caption='Uploaded Image', use_column_width=True, width=300)
                frame = np.array(image)

                save_folder = create_enrollment_folder(name)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                img_path = os.path.join(save_folder, f"{name}_{timestamp}_upload.png")
                success = cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

                if success:
                    st.success(f"✅ Enrollment image saved: {img_path}")
                else:
                    st.error("❌ Failed to save uploaded image.")

elif page == "Mark Attendance":
    st.header("✅ Mark Attendance")
    encodings, names = load_known_faces()

    if not encodings:
        st.warning("No enrolled faces found. Please enroll first.")
    else:
        method = st.radio("Select Attendance Method", ["Webcam", "Upload Photo", "Upload Video"])

        if method == "Webcam":
            if "attend_active" not in st.session_state:
                st.session_state.attend_active = False

            start_btn = st.button("▶️ Start Camera", key="start_attendance_btn")
            stop_btn = st.button("❌ Stop Camera", key="stop_attendance_btn")
            stframe = st.empty()

            if start_btn:
                st.session_state.attend_active = True

            if stop_btn:
                st.session_state.attend_active = False

            if st.session_state.attend_active:
                cap = cv2.VideoCapture(0)
                marked = set()

                if cap.isOpened():
                    st.info("Camera running. Press 'Stop Camera' to end.")
                    while st.session_state.attend_active:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Failed to read from camera.")
                            break

                        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                        locations = face_recognition.face_locations(rgb)
                        encs = face_recognition.face_encodings(rgb, locations)

                        names_detected = []
                        for face_encoding in encs:
                            matches = face_recognition.compare_faces(encodings, face_encoding, tolerance=0.55)
                            name = "Unknown"
                            dist = face_recognition.face_distance(encodings, face_encoding)
                            if len(dist) > 0:
                                best = np.argmin(dist)
                                if matches[best]:
                                    name = names[best]
                                    if name not in marked and mark_attendance(name):
                                        st.success(f"✅ {name} marked present")
                                        marked.add(name)
                            names_detected.append(name)

                        # Draw face boxes
                        for (top, right, bottom, left), name in zip(locations, names_detected):
                            top *= 4; right *= 4; bottom *= 4; left *= 4
                            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                            cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")
                        time.sleep(0.03)

                    cap.release()
                    cv2.destroyAllWindows()

        elif method == "Upload Photo":
            uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_container_width=True)
                image_np = np.array(image.convert('RGB'))
                marked_names = mark_attendance_from_image(image_np, encodings, names)
                if marked_names:
                    st.success(f"✅ Attendance marked for: {', '.join(marked_names)}")
                else:
                    st.warning("No known faces detected in the uploaded image.")

        elif method == "Upload Video":
            uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
            if uploaded_video is not None:
                st.video(uploaded_video)

                temp_path = "temp_video.mp4"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_video.read())

                with st.spinner("Processing video for face recognition..."):
                    marked_names = mark_attendance_from_video(temp_path, encodings, names)
                    os.remove(temp_path)

                    if marked_names:
                        st.success(f"✅ Attendance marked for: {', '.join(marked_names)}")
                    else:
                        st.warning("No known faces detected in the video.")
