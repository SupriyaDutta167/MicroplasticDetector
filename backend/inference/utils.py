"""
inference/utils.py
Helpers for drawing boxes and computing size estimates.
"""

import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

def draw_boxes_on_image(image_bgr, detections, class_names=None, thickness=2, font_scale=0.5):
    """
    Draw detection boxes returned by YOLO model inference.
    detections: list of dicts with keys: 'xyxy' ([xmin, ymin, xmax, ymax]), 'conf', 'class'
    image_bgr: opencv image (BGR)
    Returns annotated image (BGR).
    """
    img = image_bgr.copy()
    for det in detections:
        x1, y1, x2, y2 = map(int, det['xyxy'])
        conf = det.get('conf', 0)
        cls = det.get('class', 0)
        label = f"{class_names[cls] if class_names else cls} {conf:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), thickness)
        cv2.putText(img, label, (x1, max(y1 - 6, 0)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 1, cv2.LINE_AA)
    return img

def estimate_sizes(detections, mm_per_pixel=None):
    """
    Estimate object sizes from bounding boxes. If mm_per_pixel provided, convert to mm.
    Returns list of estimated widths (pixels) and widths_mm if mm_per_pixel provided.
    detections: list of dicts with 'xyxy'
    """
    sizes_px = []
    sizes_mm = []
    for det in detections:
        x1, y1, x2, y2 = det['xyxy']
        width_px = abs(x2 - x1)
        height_px = abs(y2 - y1)
        mean_px = (width_px + height_px) / 2.0  # use mean dimension as proxy
        sizes_px.append(mean_px)
        sizes_mm.append(mean_px * mm_per_pixel if mm_per_pixel else None)
    return sizes_px, sizes_mm

def detections_to_summary(detections, mm_per_pixel=None):
    """
    Return summary dict: count, sizes_px, sizes_mm, mean_size_mm, etc.
    """
    sizes_px, sizes_mm = estimate_sizes(detections, mm_per_pixel)
    count = len(detections)
    mean_px = float(np.mean(sizes_px)) if sizes_px else 0.0
    valid_mm = [s for s in sizes_mm if s is not None]
    mean_mm = float(np.mean(valid_mm)) if valid_mm else None

    return {
        "count": count,
        "sizes_px": sizes_px,
        "sizes_mm": sizes_mm,
        "mean_px": mean_px,
        "mean_mm": mean_mm
    }
