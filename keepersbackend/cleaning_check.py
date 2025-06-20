import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from ultralytics import YOLO

yolo_model = YOLO("yolov8n.pt")

def load_image(path):
    return Image.open(path).convert("RGB")

def align_images_orb(img1, img2):
    orb = cv2.ORB_create(1000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    if len(matches) < 4:
        raise ValueError("Not enough ORB matches.")
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    return cv2.warpPerspective(img2, H, (img1.shape[1], img1.shape[0]))

def generate_preview(input_path, output_path, size=(300, 300)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.open(input_path)
    img.thumbnail(size)
    img.save(output_path, "JPEG")

def extract_detections(yolo_result):
    detections = []
    for box in yolo_result.boxes:
        cls_id = int(box.cls[0])
        label = yolo_model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detections.append({
            "label": label,
            "bbox": (x1, y1, x2, y2)
        })
    return detections

def visual_diff_combined(ref_path, post_path, output_path):
    img1 = cv2.imread(ref_path)
    img2 = cv2.imread(post_path)

    if img1 is None or img2 is None:
        print(f"[ERROR] Failed to load images: {ref_path}, {post_path}")
        return

    try:
        img2 = align_images_orb(img1, img2)
    except Exception as e:
        print(f"[ERROR] Alignment failed: {e}")
        return

    annotated = img2.copy()

    lab1 = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)
    lab2 = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
    l1, _, _ = cv2.split(lab1)
    l2, _, _ = cv2.split(lab2)

    diff = cv2.absdiff(l1, l2)
    blur = cv2.GaussianBlur(diff, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 35, 255, cv2.THRESH_BINARY)

    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    cleaned = cv2.dilate(cleaned, kernel, iterations=1)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        aspect_ratio = w / h if h != 0 else 0

        if area < 400 or w < 20 or h < 20:
            continue
        if area < 1000:
            continue
        if aspect_ratio < 0.3 or aspect_ratio > 3.0:
            continue
        if x == 0 or y == 0 or x + w >= annotated.shape[1] or y + h >= annotated.shape[0]:
            continue

        boxes.append((x, y, w, h))

    def is_inside(box_a, box_b):
        ax, ay, aw, ah = box_a
        bx, by, bw, bh = box_b
        return (ax > bx and ay > by and ax + aw < bx + bw and ay + ah < by + bh)

    filtered_boxes = []
    for i, box in enumerate(boxes):
        if not any(is_inside(box, other) for j, other in enumerate(boxes) if i != j):
            filtered_boxes.append(box)

    yolo_post = yolo_model(img2)[0]
    yolo_ref = yolo_model(img1)[0]

    yolo_detections_post = extract_detections(yolo_post)
    yolo_detections_ref = extract_detections(yolo_ref)

    def relaxed_iou_overlap(diff_box, det_box, threshold=0.1):
        dx, dy, dw, dh = diff_box
        bx1, by1, bx2, by2 = det_box
        dx1, dy1, dx2, dy2 = dx, dy, dx + dw, dy + dh
        ix1, iy1 = max(dx1, bx1), max(dy1, by1)
        ix2, iy2 = min(dx2, bx2), min(dy2, by2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
        union = (dx2 - dx1) * (dy2 - dy1) + (bx2 - bx1) * (by2 - by1) - inter
        return (inter / union) > threshold if union > 0 else False

    def get_label(diff_box, detections):
        dx, dy, dw, dh = diff_box
        dx1, dy1, dx2, dy2 = dx, dy, dx + dw, dy + dh
        for det in detections:
            bx1, by1, bx2, by2 = det['bbox']
            if relaxed_iou_overlap((dx, dy, dw, dh), (bx1, by1, bx2, by2)):
                return det['label']
        return None

    for (x, y, w, h) in filtered_boxes:
        diff_box = (x, y, w, h)

        in_post = any(relaxed_iou_overlap(diff_box, det['bbox']) for det in yolo_detections_post)
        in_ref = any(relaxed_iou_overlap(diff_box, det['bbox']) for det in yolo_detections_ref)

        if in_post and not in_ref:
            label = get_label(diff_box, yolo_detections_post)
            tag = f"Added - {label}" if label else "Different"
            color = (0, 255, 0) if label else (255, 255, 0)
        elif in_ref and not in_post:
            label = get_label(diff_box, yolo_detections_ref)
            tag = f"Missing - {label}" if label else "Different"
            color = (0, 0, 255) if label else (255, 255, 0)
        elif not in_post and not in_ref:
            tag = "Different"
            color = (255, 255, 0)
        else:
            continue  # Skip Changed

        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 10)
        cv2.putText(annotated, tag, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.8, color, 3)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    success = cv2.imwrite(output_path, annotated)
    print(f"[✓] Annotated image saved: {output_path}")
    print(f"[✓] Save success? {success}")

def inspect_cleaning_job(ref_path, post_path, job_id="job"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    annotated_path = os.path.join("annotated", f"{job_id}_{ts}_annotated.jpg")
    preview_dir = os.path.join("annotated", "previews")
    ref_preview = os.path.join(preview_dir, f"{job_id}_{ts}_ref.jpg")
    post_preview = os.path.join(preview_dir, f"{job_id}_{ts}_post.jpg")

    visual_diff_combined(ref_path, post_path, annotated_path)
    generate_preview(ref_path, ref_preview)
    generate_preview(post_path, post_preview)

    return {
        "annotated_image": annotated_path,
        "ref_preview": ref_preview,
        "post_preview": post_preview
    }

if __name__ == "__main__":
    ref_dir = "batch/reference"
    post_dir = "batch/postclean"
    files = sorted(os.listdir(ref_dir))

    for i, fname in enumerate(files):
        ref_path = os.path.join(ref_dir, fname)
        post_path = os.path.join(post_dir, fname)
        if os.path.exists(ref_path) and os.path.exists(post_path):
            inspect_cleaning_job(ref_path, post_path, job_id=f"batch_job_{i+1:03d}")
