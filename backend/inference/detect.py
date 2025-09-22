"""
detect.py
Use a trained YOLOv8 model to run inference on images and save visualized result.

Example usage:
    python detect.py --model runs/train/microplastic_experiment/weights/best.pt --image input.jpg --out output.jpg
"""

import argparse
from ultralytics import YOLO
import cv2
from pathlib import Path
from backend.inference.utils import draw_boxes_on_image, detections_to_summary

# Set WATER_ML globally or pass as argument if needed
WATER_ML = 100  # Adjust to your sample size

def run_inference(model_path, image_path, output_image_path=None, conf_thresh=0.25, iou=0.45, mm_per_pixel=None):
    model = YOLO(model_path)
    results = model.predict(source=str(image_path), conf=conf_thresh, iou=iou, max_det=300, verbose=False)
    
    # ultralytics returns list of Results, take first
    res = results[0]
    boxes = res.boxes.xyxy.cpu().numpy() if hasattr(res, 'boxes') else []
    confs = res.boxes.conf.cpu().numpy() if hasattr(res, 'boxes') else []
    cls = res.boxes.cls.cpu().numpy().astype(int) if hasattr(res, 'boxes') else []

    detections = []
    for b, c, cf in zip(boxes, cls, confs):
        x1, y1, x2, y2 = b.tolist()
        detections.append({"xyxy": [x1, y1, x2, y2], "class": int(c), "conf": float(cf)})

    # read image with OpenCV
    img = cv2.imread(str(image_path))
    annotated = draw_boxes_on_image(img, detections, class_names=model.names)
    if output_image_path:
        cv2.imwrite(str(output_image_path), annotated)

    # Generate summary
    summary = detections_to_summary(detections, mm_per_pixel)
    summary["count"] = len(detections)

    # Calculate percent plastic and water
    total = WATER_ML + summary["count"]
    summary["percent_plastic"] = round((summary["count"] / total) * 100, 2) if total > 0 else 0
    summary["percent_water"] = round((WATER_ML / total) * 100, 2) if total > 0 else 0

    # attach per-detection sizes
    for det, px, mm in zip(detections, summary["sizes_px"], summary["sizes_mm"]):
        det['size_px'] = px
        det['size_mm'] = mm

    return {
        "detections": detections,
        "summary": summary,
        "annotated_image": str(output_image_path) if output_image_path else None
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--image", type=str, required=True)
    parser.add_argument("--out", type=str, default="out.jpg")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--mmperpx", type=float, default=None)
    args = parser.parse_args()

    out = run_inference(
        model_path=args.model,
        image_path=args.image,
        output_image_path=args.out,
        conf_thresh=args.conf,
        mm_per_pixel=args.mmperpx
    )

    print(out)
