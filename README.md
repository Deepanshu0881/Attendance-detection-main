
# 🧠 Face Recognition Attendance System

A **real-time face recognition-based attendance system** built using Python, Streamlit, OpenCV, and face_recognition (dlib). The app allows for student enrollment, live/video-based attendance tracking, and failure detection for unknown faces.

---

## 🔧 Tech Stack

- **Backend**: Python 3.10  
- **Web Framework**: [Streamlit](https://streamlit.io)  
- **Face Recognition**: [face_recognition](https://github.com/ageitgey/face_recognition) (built on top of dlib)  
- **Image Processing**: [OpenCV](https://opencv.org/) (`opencv-python`)  
- **Numerical Operations**: NumPy  
- **System Dependencies**: CMake, C++ Build Tools (required by dlib)

---

## ⚙️ Prerequisites

Make sure the following are installed on your system:

- Python (3.10 recommended)
- pip (Python package manager)
- CMake
- C++ Build Tools (Visual Studio Build Tools on Windows)

---

## 🚀 Getting Started

### 📁 Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/face-recognition-attendance.git
cd face-recognition-attendance
```

### 🧪 Step 2: Create and Activate Virtual Environment

**(Only required for first-time setup)**

```bash
python -m venv venv
```

> 🛡️ On Windows, allow script execution if needed:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Unix/macOS (if applicable)
source venv/bin/activate
```

### 📦 Step 3: Install Dependencies

```bash
pip install --no-cache-dir -r requirements.txt
```

> ⚠️ **Facing issues with `dlib` installation?**  
Use the provided `.whl` file for your system and install manually:

```bash
pip install path\to\dlib‑19.xx.x‑cp310‑cp310‑win_amd64.whl
```

> If an error still occurs, try installing packages one-by-one manually.

---

## ▶️ Running the App

Once your environment is ready, run the Streamlit app:

```bash
streamlit run app.py
```

---

## 🔁 Subsequent Runs

If the virtual environment already exists:

```powershell
# Optional (if admin permissions are required again)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate environment
venv\Scripts\activate

# Run app
streamlit run app.py
```

---

## ❌ Deactivating Virtual Environment

To exit the virtual environment:

```bash
deactivate
```

---

## 💡 Features

- 🎓 **Student Enrollment** via image and live camera
- 📷 **Attendance Detection** from live camera, group photo and video
- 🧠 **Real-time Face Matching**
- 🚫 **Unknown Face Handling**
- 📋 **Attendance Logs**

---

## 🛠️ Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](LICENSE)
