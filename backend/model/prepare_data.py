from utils import convert_annotations_csv_to_yolo

convert_annotations_csv_to_yolo(
    "backend/model/data/train/_annotations.csv",
    "backend/model/data/train"
)

convert_annotations_csv_to_yolo(
    "backend/model/data/valid/_annotations.csv",
    "backend/model/data/valid"
)
