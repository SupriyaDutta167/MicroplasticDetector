# backend/server/esp32_stream.py
import cv2
import time
import urllib.request
import numpy as np
from fastapi.responses import StreamingResponse, JSONResponse

ESP32_URL = "http://10.190.245.167/"
WATER_ML = 100

stats = {
    "objects": 0,
    "grams_per_ml": 0.0,
    "percent_plastic": 0.0,
    "water_ml": WATER_ML
}

def get_frame_and_update_stats():
    global stats
    try:
        img_resp = urllib.request.urlopen(ESP32_URL + "cam-lo.jpg")
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)

        # contour analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(cv2.GaussianBlur(gray, (11, 11), 0), 30, 150, 3)
        dilated = cv2.dilate(canny, (1, 1), iterations=2)
        cnt, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        objects = len(cnt)
        grams_per_ml = objects / WATER_ML if WATER_ML > 0 else 0
        percent_plastic = (objects / (objects + WATER_ML)) * 100 if (objects + WATER_ML) > 0 else 0

        stats.update({
            "objects": objects,
            "grams_per_ml": round(grams_per_ml, 3),
            "percent_plastic": round(percent_plastic, 2),
            "water_ml": WATER_ML
        })

        return frame
    except Exception as e:
        print("ESP32 error:", e)
        return np.zeros((240, 320, 3), dtype=np.uint8)

def gen_frames():
    while True:
        frame = get_frame_and_update_stats()
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
        )
        time.sleep(0.1)
