import io
import os
import base64
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
YOLO_MODEL_PATH = os.path.join(WEIGHTS_DIR, "yolov8n.pt")

try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
except Exception:
    yolo_model = YOLO("yolov8n.pt")


def predict_text_sentiment(text: str) -> dict:
    positive_words = ["good", "great", "awesome", "excellent", "happy", "love", "best"]
    negative_words = ["bad", "worst", "poor", "terrible", "sad", "hate", "horrible"]

    lowered_text = text.lower()
    pos_count = sum(1 for word in positive_words if word in lowered_text)
    neg_count = sum(1 for word in negative_words if word in lowered_text)

    if pos_count > neg_count:
        sentiment = "Positive"
        confidence = 0.88
    elif neg_count > pos_count:
        sentiment = "Negative"
        confidence = 0.85
    else:
        sentiment = "Neutral"
        confidence = 0.50

    return {
        "text": text,
        "sentiment": sentiment,
        "confidence": confidence
    }


def predict_image_voids(image_bytes: bytes) -> dict:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = yolo_model(image)

        draw = ImageDraw.Draw(image)
        detections = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = [round(float(x), 2) for x in box.xyxy[0].tolist()]

                # Detection details
                detections.append({
                    "class": cls_id,
                    "confidence": conf,
                    "bbox": xyxy
                })

                # Draw Bounding Box on Image
                draw.rectangle(xyxy, outline="red", width=3)
                draw.text((xyxy[0], max(0, xyxy[1] - 10)), f"Class {cls_id} ({round(conf*100)}%)", fill="red")

        # Convert Annotated Image to Base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return {
            "status": "success",
            "total_detections": len(detections),
            "detections": detections,
            "annotated_image": f"data:image/jpeg;base64,{img_str}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }