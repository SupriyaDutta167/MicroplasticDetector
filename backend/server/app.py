import os
import time
import urllib.request
import numpy as np
import cv2
import csv
import datetime
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import threading
import requests

from backend.inference.detect import run_inference
from backend.server.esp32_handler import save_image_from_post

# ================================
# Config
# ================================
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
MODEL_PATH = BASE_DIR / "runs/train/microplastic_experiment/weights/best.pt"
MM_PER_PIXEL = 0.05
WATER_ML = 100

# Camera URL (default to your IP, can override with env var)
CAM_URL = os.getenv("CAM_URL", "http://10.190.245.60:8080/video")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ================================
# FastAPI app
# ================================
app = FastAPI(title="Microplastic Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# Latest detection info
# ================================
latest_info = {
    "image_path": None,
    "annotated_path": None,
    "result": None
}

# ================================
# Upload & Detection Routes
# ================================
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    out_path = UPLOAD_DIR / file.filename
    save_image_from_post(contents, out_path)

    annotated_out = RESULTS_DIR / f"annotated_{file.filename}"
    if MODEL_PATH.exists():
        res = run_inference(
            str(MODEL_PATH), str(out_path), str(annotated_out), mm_per_pixel=MM_PER_PIXEL
        )
        total_objects = res['summary']['count']
        percent_plastic = (total_objects / (total_objects + WATER_ML)) * 100 if (total_objects + WATER_ML) > 0 else 0
        percent_water = 100 - percent_plastic
        res['summary'].update({
            "percent_plastic": round(percent_plastic, 2),
            "percent_water": round(percent_water, 2)
        })

        latest_info.update({
            "image_path": str(out_path),
            "annotated_path": str(annotated_out),
            "result": res
        })
    else:
        latest_info.update({
            "image_path": str(out_path),
            "annotated_path": None,
            "result": {"msg": "Model not found - image saved."}
        })
    return {"status": "ok", "filename": file.filename}

@app.post("/detect")
async def detect_image(filename: str, conf: float = 0.25):
    image_path = UPLOAD_DIR / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    annotated_out = RESULTS_DIR / f"annotated_{filename}"
    if not Path(MODEL_PATH).exists():
        raise HTTPException(status_code=500, detail="Trained model not found on server")

    res = run_inference(
        str(MODEL_PATH), str(image_path), str(annotated_out),
        conf_thresh=conf, mm_per_pixel=MM_PER_PIXEL
    )
    total_objects = res['summary']['count']
    percent_plastic = (total_objects / (total_objects + WATER_ML)) * 100 if (total_objects + WATER_ML) > 0 else 0
    percent_water = 100 - percent_plastic
    res['summary'].update({
        "percent_plastic": round(percent_plastic, 2),
        "percent_water": round(percent_water, 2)
    })

    latest_info.update({
        "image_path": str(image_path),
        "annotated_path": str(annotated_out),
        "result": res
    })
    return {"status": "ok", "result": res}

@app.get("/api/latest")
async def get_latest():
    res = latest_info['result']
    annotated_path = latest_info['annotated_path']
    image_url = None
    if annotated_path:
        image_url = f"/image/{Path(annotated_path).name}"
    elif latest_info['image_path']:
        image_url = f"/image/{Path(latest_info['image_path']).name}"

    stats = {}
    if isinstance(res, dict) and 'summary' in res:
        summary = res['summary']
        stats['count'] = summary.get('count', 0)
        stats['percent_plastic'] = summary.get('percent_plastic', 0)
        stats['percent_water'] = summary.get('percent_water', 100)

    return {"imageUrl": image_url, "stats": stats}

@app.get("/image/{image_name}")
async def serve_image(image_name: str):
    candidate = RESULTS_DIR / image_name
    if not candidate.exists():
        candidate = UPLOAD_DIR / image_name
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(candidate, media_type="image/jpeg")

# ================================
# Live Feed + Stats (HTTP MJPEG)
# ================================
esp32_stats = {
    "objects": 0,
    "grams_per_ml": 0.0,
    "percent_plastic": 0.0,
    "percent_water": 100.0,
    "water_ml": WATER_ML
}

LOG_FILE = BASE_DIR / "live_log.csv"
is_logging = False  # flag

def fetch_esp32_frame():
    """
    Fetches a frame from the camera stream and applies microplastic detection.
    """
    global esp32_stats
    try:
        # Fetch MJPEG frame manually
        stream = requests.get(CAM_URL, stream=True, timeout=5)
        bytes_data = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                break
        else:
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
    except Exception as e:
        print(f"Camera fetch error: {e}")
        frame = np.zeros((240, 320, 3), dtype=np.uint8)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(cv2.GaussianBlur(gray, (11, 11), 0), 30, 150)
    dilated = cv2.dilate(canny, (1, 1), iterations=2)
    cnt, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    objects = len(cnt)
    grams_per_ml = objects / WATER_ML if WATER_ML > 0 else 0
    percent_plastic = (objects / (objects + WATER_ML)) * 100 if (objects + WATER_ML) > 0 else 0
    percent_water = 100 - percent_plastic

    # Draw bounding boxes + size
    for c in cnt:
        x, y, w, h = cv2.boundingRect(c)
        if w > 5 and h > 5:
            size_mm = round((w + h) / 2 * MM_PER_PIXEL, 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{size_mm} mm", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    esp32_stats.update({
        "objects": objects,
        "grams_per_ml": round(grams_per_ml, 3),
        "percent_plastic": round(percent_plastic, 2),
        "percent_water": round(percent_water, 2),
        "water_ml": WATER_ML
    })

    return frame

def gen_esp32_frames():
    while True:
        frame = fetch_esp32_frame()
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
        )
        time.sleep(0.1)

# ================================
# CSV Logging (every 5s for 30s)
# ================================
def log_esp32_stats():
    global is_logging
    if is_logging:
        return
    is_logging = True

    start_time = time.time()

    if not LOG_FILE.exists():
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'objects', 'grams_per_ml',
                             'percent_plastic', 'percent_water', 'water_ml'])

    while time.time() - start_time < 30:
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                esp32_stats.get('objects', 0),
                esp32_stats.get('grams_per_ml', 0.0),
                esp32_stats.get('percent_plastic', 0.0),
                esp32_stats.get('percent_water', 100.0),
                esp32_stats.get('water_ml', WATER_ML)
            ])
        time.sleep(5)

    is_logging = False
    print(f"✅ Logging finished. Saved in {LOG_FILE}")

# ================================
# Endpoints
# ================================
@app.get("/esp32/video_feed")
async def esp32_video_feed():
    if not is_logging:
        logging_thread = threading.Thread(target=log_esp32_stats, daemon=True)
        logging_thread.start()
    return StreamingResponse(
        gen_esp32_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/esp32/stats")
async def esp32_stats_endpoint():
    return JSONResponse(content=esp32_stats)

# ================================
# Run server
# ================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server.app:app", host="0.0.0.0", port=8000, reload=True)
