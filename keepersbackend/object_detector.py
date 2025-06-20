from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # Replace with your trained model if available

def detect_objects(image_path):
    results = model(image_path)
    names = model.names
    objects = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            name = names[cls_id]
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            objects.append({"label": name, "confidence": conf, "box": bbox})
    
    return objects
