# 🔬 Microplastic Detector

**AI-powered microplastic detection & water-quality dashboard**  
Works with **ESP32-CAM**, microscope cameras, or phone cameras.  
Backend (**FastAPI + OpenCV + YOLOv8**) performs detection and sizing; frontend (**React**) shows live feed, charts, and alerts. Data is logged to **CSV**.

---

## 📑 Table of Contents
- [What this project does](#-what-this-project-does)  
- [Features](#-features)  
- [Architecture & file layout](#-architecture--file-layout)  
- [Frontend stack & tech](#-frontend-stack--tech)  
- [Backend stack & tech](#-backend-stack--tech)  
- [AI model & training](#-ai-model--training)  
- [Detection & sizing pipeline](#-detection--sizing-pipeline)  
- [Calibration (mm_per_pixel)](#-calibration-mm_per_pixel)  
- [API (endpoints & examples)](#-api-endpoints--examples)  
- [Running locally (dev)](#-running-locally-dev)  
- [Data logging (CSV)](#-data-logging-csv)  
- [Limitations & best practices](#-limitations--best-practices)  
- [Troubleshooting](#-troubleshooting)  
- [Security & production notes](#-security--production-notes)  
- [Dataset info](#-dataset-information)  
- [How the AI detects](#-how-the-ai-detects-plain-language)  
- [License & credits](#-license--credits)  

---

## 📌 What this project does
A full-stack system to detect **microplastic particles** in images or live camera streams and present water quality metrics on a modern React dashboard.

- Accepts **image uploads** (single-frame detection)  
- Streams **live camera** (ESP32 / phone / microscope)  
- Uses **YOLOv8 object detection** for bounding-box-based sizing  
- Converts **pixel sizes → mm** with a calibration factor  
- Computes **particle count** and % microplastic vs water  
- Displays results as **pie chart + stats**  
- Logs **live statistics to CSV**  
- Plays **alert sound** when plastic% exceeds threshold (10%)  

---

## ✨ Features
- **Upload & detect images** → `/upload`, `/detect`  
- **Live camera streaming** → `/esp32/video_feed`  
- **Live stats** → `/esp32/stats`, `/api/latest`  
- **Annotated result images** → `/image/{name}`  
- **CSV logging** of live stats (configurable interval)  
- **React dashboard** with pie chart, stats, and alerts  

---

## 🏗 Architecture & file layout
```
microplastic-detector/
├─ backend/
│  ├─ server/
│  │  ├─ app.py                # FastAPI main (endpoints, logging)
│  │  └─ esp32_handler.py
│  ├─ inference/
│  │  ├─ detect.py             # YOLOv8 inference wrapper
│  │  └─ utils.py              # draw_boxes, detections_to_summary
│  ├─ uploads/
│  └─ results/
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ StatsPanel.jsx
│  │  │  └─ ImageViewer.jsx
│  │  ├─ pages/Dashboard.jsx
│  │  └─ api/api.js
│  ├─ package.json
│  └─ vite.config.js
├─ runs/                        # YOLO training outputs
├─ README.md
└─ .gitignore
```

---

## 🎨 Frontend stack & tech
- **React + Vite**  
- **Recharts** → pie chart visualization  
- **Axios** → API calls  
- **CSS** → styling  

Example dependencies:
```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "axios": "^1.x",
    "recharts": "^2.x"
  }
}
```

---

## ⚙️ Backend stack & tech
- **FastAPI** (with uvicorn)  
- **YOLOv8 (Ultralytics)** for detection/training  
- **OpenCV + NumPy** for image processing  
- **Requests/urllib** for camera streams  
- **CSV logging** (live_log.csv)  

Example `requirements.txt`:
```
fastapi
uvicorn[standard]
opencv-python
numpy
ultralytics
requests
python-multipart
pillow
```

---

## 🧠 AI model & training
- **Model**: YOLOv8 (Ultralytics)  
- **Training**: 50 epochs, COCO/YOLO-style dataset  
- **Command**:
```bash
yolo task=detect mode=train model=yolov8s.pt data=data.yaml epochs=50 imgsz=640 batch=16
```

Dataset:
```
images/train/*.jpg, labels/train/*.txt
images/val/*.jpg, labels/val/*.txt
```

---

## 🔄 Detection & sizing pipeline
1. **Upload / Stream frame**  
2. **Run YOLOv8 inference**  
3. **Bounding boxes → size (px)**  
4. **Convert px → mm** (if calibrated)  
5. **Compute % plastic** vs water  
6. **Save annotated image + stats**  

---

## 📏 Calibration (mm_per_pixel)
1. Place object of **known length** in view  
2. Measure in **pixels**  
3. Compute:  
   ```
   mm_per_pixel = known_length_mm / measured_length_px
   ```
4. Set value in **app.py** or env var  

---

## 🔌 API (endpoints & examples)
- **POST /upload** → upload image  
- **POST /detect** → run detection  
- **GET /api/latest** → latest stats + image  
- **GET /esp32/video_feed** → MJPEG stream  
- **GET /esp32/stats** → live stats  

Example:
```bash
curl -F "file=@sample.jpg" http://localhost:8000/upload
```

Response:
```json
{
  "imageUrl": "/image/annotated_sample.jpg",
  "stats": { "count": 12, "percent_plastic": 10.7 }
}
```

---

## 🖥 Running locally (dev)
### Backend
```bash
python -m venv .venv
source .venv/bin/activate        # mac/linux
.venv\Scriptsctivate           # windows

pip install -r backend/requirements.txt
uvicorn backend.server.app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open → `http://localhost:5173`

---

## 📊 Data logging (CSV)
- **File**: `backend/live_log.csv`  
- **Columns**: timestamp, objects, grams_per_ml, percent_plastic, percent_water, water_ml  
- Default: logs every **5s**  

---

## ⚠️ Limitations & best practices
- Sizing depends on **good calibration** & resolution  
- Small particles may be **below detection threshold**  
- **False positives** from bubbles/debris possible  
- Use **GPU** for faster inference  
- Ensure **even lighting** and clean background  

---

## 🛠 Troubleshooting
- **No stream** → check MJPEG/RTSP format  
- **CSV not writing** → check file permissions  
- **Model not found** → set `MODEL_PATH` to trained weights  
- **Poor detection** → retrain with more samples / longer epochs  

---

## 🔒 Security & production notes
- Do **not expose camera URLs** publicly  
- Add **auth** for APIs in production  
- Use **reverse proxy (nginx)** + process manager  

---

## 📂 Dataset information
- Collect images in consistent conditions  
- Label bounding boxes (YOLO format)  
- Split → **80% train / 20% val**  
- Use background images to reduce false positives  

---

## 🧾 How the AI detects (plain language)
- YOLOv8 scans the image with learned features  
- Outputs bounding boxes + confidence scores  
- Boxes → size estimates → particle count  
- Backend → aggregates → % plastic + stats  

---

## 📜 License & credits
**MIT License © 2025**

**Credits**:  
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)  
- [OpenCV](https://opencv.org/) & NumPy  
- [FastAPI](https://fastapi.tiangolo.com/)  
- [React](https://react.dev/) & Recharts  
