def convert_annotations_csv_to_yolo(csv_file, output_dir):
    """
    Convert CSV annotations to YOLO format.
    Saves .txt labels in <output_dir>/labels/
    """
    import os, pandas as pd
    df = pd.read_csv(csv_file)

    labels_dir = os.path.join(output_dir, "labels")
    os.makedirs(labels_dir, exist_ok=True)

    for _, row in df.iterrows():
        filename = row['filename']
        width, height = row['width'], row['height']
        xmin, ymin, xmax, ymax = row['xmin'], row['ymin'], row['xmax'], row['ymax']

        class_id = 0  # only 1 class = microplastic

        # YOLO normalized values
        x_center = (xmin + xmax) / 2 / width
        y_center = (ymin + ymax) / 2 / height
        w = (xmax - xmin) / width
        h = (ymax - ymin) / height

        label_file = os.path.join(labels_dir, filename.rsplit(".", 1)[0] + ".txt")
        with open(label_file, "a") as f:
            f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")

    print(f"[INFO] Labels saved in {labels_dir}")
