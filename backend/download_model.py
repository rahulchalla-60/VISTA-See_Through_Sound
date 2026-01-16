from ultralytics import YOLO

# This will automatically download yolov8n.pt if not present
model = YOLO('yolov8n.pt')
print("Model downloaded successfully!")
print(f"Model path: {model.ckpt_path}")
