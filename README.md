🔬 Microplastic Detector — README

AI-powered microplastic detection & water-quality dashboard.
Works with ESP32-CAM, microscope cameras, or phone cameras. Backend (FastAPI + OpenCV + YOLOv8) performs detection and sizing; frontend (React) shows live feed, charts and alerts. Data logged to CSV.

Table of contents

What this project does

Features

Architecture & file layout

Frontend stack & tech

Backend stack & tech

AI model & training (50 epochs)

How detection & sizing works (pipeline)

Calibration: mm_per_pixel (how to set)

API (endpoints & examples)

Running locally (dev) — quick start

Data logging (CSV)

Limitations & best practices

Troubleshooting

License & credits

What this project does

A full-stack system to detect microplastic particles in images or live camera streams and present water quality metrics on a modern React dashboard. It:

Accepts image uploads (single-frame detection).

Streams live camera (ESP32 / phone / microscope) and runs contour/object analysis + bounding boxes.

Uses a trained YOLOv8 object detector for particle detection and bounding-box-based sizing.

Converts pixel sizes to mm with a calibration factor (mm_per_pixel).

Computes particle count and percent microplastic vs water; displays a pie chart and detailed stats.

Logs live statistics to CSV regularly for later analysis.

Emits a client-side audio alert when plastic% exceeds threshold (10%).

Features

Upload & detect images (/upload, /detect)

Poll latest detection (/api/latest) — returns image URL + stats

Live streaming endpoint (/esp32/video_feed) for camera MJPEG/HTTP or IP camera

Live stats endpoint (/esp32/stats) for dashboard polling

Annotated result images saved in results/ and served via /image/{name}

CSV logging of live stats at fixed intervals (configurable in code)

UI: React dashboard with pie chart, count, percent, and color-coded quality

Architecture & file layout (example)
microplastic-detector/
├─ backend/
│  ├─ server/
│  │  ├─ app.py                # FastAPI main (endpoints, live feed, logging)
│  │  └─ esp32_handler.py
│  ├─ inference/
│  │  ├─ detect.py             # wrapper that runs YOLOv8 inference
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
├─ runs/                        # training outputs (YOLO)
├─ README.md
└─ .gitignore

Frontend — technologies & notes

Framework: React + Vite

Charts: Recharts (pie chart)

HTTP: axios

Styling: CSS (separate Dashboard.css)

Behavior: Polls backend endpoints for latest data or live stats; displays annotated image (served by backend) or video stream URL.

Recommended package.json deps (example):

{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "axios": "^1.x",
    "recharts": "^2.x"
  }
}

Backend — technologies & notes

Framework: FastAPI (uvicorn for dev server)

Model: Ultralytics YOLOv8 (ultralytics Python package) for inference/training

Image processing: OpenCV (cv2) & numpy

HTTP requests (camera reads): requests (for MJPEG streams) or urllib (older code)

Logging: CSV writer (writes live_log.csv in backend folder)

CORS: configured in app for http://localhost:5173 (adjust for production)

Recommended Python packages (requirements.txt example):

fastapi
uvicorn[standard]
opencv-python
numpy
ultralytics
requests
python-multipart
pillow

AI model & training (the model used)

Model family: Ultralytics YOLOv8 (you use ultralytics.YOLO in detect.py)

Training configuration used: 50 epochs (as you requested). Typical train command example:

# example using ultralytics CLI
yolo task=detect mode=train model=yolov8s.pt data=data.yaml epochs=50 imgsz=640 batch=16


data.yaml should point to your dataset (train/val), and include class names (single class microplastic or multiple classes if you labeled types).

Dataset structure: COCO-like or YOLOv8-friendly:

images/train/*.jpg, labels/train/*.txt

images/val/*.jpg, labels/val/*.txt

Label format: YOLO text files (class x_center y_center width height) normalized to image size OR COCO JSON (either works with ultralytics).

Training notes

Use transfer learning: start from yolov8s.pt or yolov8n.pt weights to shorten convergence time.

Augmentations (flip, scale, color jitter) help with generalization — YOLOv8 has built-in augmentation config.

Evaluate using mAP and visual inspection of predictions.

Use GPU for reasonable training time (50 epochs on CPU will be very slow).

How detection & sizing works (pipeline)

Upload / Run inference

POST /upload saves the file (backend uploads/) then calls run_inference() (see detect.py) which:

Loads YOLOv8 model: model = YOLO(model_path)

Calls model.predict(source=image, conf=conf_thresh) to get detections

Extracts boxes (xyxy), class ids, confidences

Draws boxes on image via draw_boxes_on_image() (utils)

Computes detections_to_summary() which returns:

count — number of detections

sizes_px — per-detection size estimate (mean of width & height in pixels)

sizes_mm — per-detection sizes converted to mm using mm_per_pixel when provided

mean_px, mean_mm

Sizing

Sizing uses bounding-box dimensions. The code takes width w = x2 - x1, height h = y2 - y1, uses a proxy size = (w + h) / 2.

If MM_PER_PIXEL (calibration) is provided, size_mm = size_px * MM_PER_PIXEL.

Percent microplastic

Backend converts particle count to percent: percent_plastic = (count / (count + WATER_ML)) * 100 (water ml is configured).

The response attachment summary includes count, percent_plastic, percent_water, sizes_mm (if calibrated).

Frontend

Polls /api/latest (or /esp32/stats for live) and renders the PieChart and numbers. If percent_plastic > 10 the UI flags poor quality and plays beep.

Note: This approach uses bounding boxes to estimate size — for irregular particles, this is an approximation (width/height proxy).

Calibration: computing mm_per_pixel

To convert pixel-measurements to real-world mm you need to calibrate:

Place an object of known length (ruler or calibration target) at the same imaging distance & zoom as your samples.

Capture an image, measure the object length in pixels (e.g., measure with an image editor or count bounding-box width).

Calculate:

mm_per_pixel = known_length_mm / measured_length_px


Put that value into MM_PER_PIXEL in app.py (or supply it to run_inference()).

API — endpoints & examples
POST /upload

Uploads an image, runs detection (if model available), saves annotated image.

Form field: file (multipart/form-data)

curl -F "file=@sample.jpg" http://localhost:8000/upload


Response: {"status":"ok","filename":"sample.jpg"}

POST /detect?filename=...&conf=0.25

Run detection on an existing upload by filename
Response: {"status":"ok","result": { ... } }

GET /api/latest

Returns the most recent detection summary + image URL (served under /image/..)
Example response:

{
  "imageUrl": "/image/annotated_sample.jpg",
  "stats": {
    "count": 12,
    "percent_plastic": 10.71,
    "percent_water": 89.29
  }
}

GET /image/{image_name}

Serves annotated image saved in results/ or uploads/

Live streaming & stats

GET /esp32/video_feed — MJPEG-style streaming response for the frontend’s <img src="..."> or <video> tag.

GET /esp32/stats — returns JSON with running stats:

{
  "objects": 5,
  "grams_per_ml": 0.05,
  "percent_plastic": 4.76,
  "percent_water": 95.24,
  "water_ml": 100
}

Running locally — quick start
Backend

Create & activate a virtual environment

python -m venv .venv
source .venv/bin/activate     # mac / linux
.venv\Scripts\activate        # windows


Install requirements

pip install -r backend/requirements.txt
# or pip install fastapi uvicorn opencv-python numpy ultralytics requests python-multipart pillow


(Optional) Set camera URL (phone IP) and calibration via environment variables:

export CAM_URL="http://10.190.245.191:8080/video"
export MM_PER_PIXEL=0.05


Run backend

python backend/server/app.py
# or using uvicorn:
uvicorn backend.server.app:app --host 0.0.0.0 --port 8000 --reload

Frontend

cd frontend

npm install

npm run dev (Vite) or npm start

Open http://localhost:5173 and configure PC_IP in Dashboard.jsx if needed.

Data logging (CSV)

The backend writes live stats into live_log.csv (in backend BASE_DIR).

Default behavior (as provided in your code): logs every 5 seconds continuously.

CSV columns: timestamp, objects, grams_per_ml, percent_plastic, percent_water, water_ml

Make sure the backend process has write permissions in the project folder.

Limitations & best practices

Sizing accuracy depends on good calibration and image resolution. Very small particles may be below camera resolution.

False positives may occur with bubbles, debris, or background artefacts. Improve dataset & augmentation to reduce this.

Lighting/contrast are critical — use diffuse even lighting, high-contrast backgrounds, and consistent imaging distance.

For production, run inference on a GPU-enabled environment for performance.

CORS and debug mode: for production, remove reload=True, restrict CORS origins, and put the app behind a reverse proxy (nginx).

Troubleshooting

Black stream / no frames: many phone streaming apps present MJPEG that OpenCV’s VideoCapture cannot decode. Use the HTTP MJPEG reader (as implemented in the repo) or use RTSP if available.

CSV not writing: check file path, permissions, and that the logging thread starts (startup event). Ensure uvicorn server has permission to write.

Model not found: ensure MODEL_PATH points to trained weights (e.g. runs/train/microplastic_experiment/weights/best.pt).

Model poor performance: retrain with more labeled samples, tune augmentations, or increase epochs beyond 50.

Example: training command

Example using ultralytics (YOLOv8):

# using ultralytics CLI
yolo task=detect mode=train model=yolov8s.pt data=data.yaml epochs=50 imgsz=640 batch=16


After training, best weights typically appear in:

runs/train/<exp_name>/weights/best.pt


Point MODEL_PATH in app.py to that file.

Security & production notes

Don’t expose camera URL/CREDENTIALS publicly. Use environment variables for secrets.

Consider authentication for API endpoints if deploying publicly.

For stability, run behind a process manager (systemd, docker-compose) and use gunicorn/uvicorn workers.

Dataset information (recommended)

Use a custom dataset of microplastic images:

Collect images under consistent imaging conditions.

Label bounding boxes around particles (YOLO format).

Typical split: 80% train / 20% val.

Include negative/background images to reduce false positives.

Public datasets for microplastics exist in literature; if you used a public dataset, include a citation in your repo (replace this section with the actual dataset info you used).

How the AI detects (plain language)

The YOLOv8 detector slides a learned set of features across the image and produces bounding boxes with confidence scores for objects it recognizes as microplastic (single-class or multi-class as trained).

Ultralitycs' post-processing (NMS) removes overlapping boxes and returns the final boxes.

Each box → size estimate → count.

Backend aggregates counts to compute ratios and saves annotated images.

License & credits

MIT License © 2025

Credits:

YOLOv8 / Ultralytics for object detection

OpenCV & NumPy for image processing

React & Recharts for frontend visualization