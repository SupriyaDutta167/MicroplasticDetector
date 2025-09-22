"""
train.py
Train YOLOv8 on your dataset (requires ultralytics package).

Usage:
    python train.py --data dataset.yaml --epochs 50 --batch 8 --img 640 --model yolov8n.pt
"""

import argparse
from ultralytics import YOLO
import os

def train(data_cfg, epochs=50, batch=8, img_size=640, model_name="yolov8n.pt", project="runs/train"):
    """
    data_cfg: path to dataset.yaml
    """
    print("Starting training with:")
    print(f" data: {data_cfg}, epochs: {epochs}, batch: {batch}, img: {img_size}, model: {model_name}")
    model = YOLO(model_name)  # uses pretrained weights
    model.train(data=data_cfg,
                epochs=epochs,
                imgsz=img_size,
                batch=batch,
                project=project,
                name="microplastic_experiment",
                exist_ok=True)
    print("Training complete. Check the `runs/train` directory for weights.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="dataset.yaml", help="dataset yaml")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--img", type=int, default=640)
    parser.add_argument("--model", type=str, default="yolov8n.pt")
    args = parser.parse_args()
    train(args.data, args.epochs, args.batch, args.img, args.model)
