from ultralytics import YOLO
import cv2
import config
import time
from datetime import datetime

class VisionEngine:
    def __init__(self, model_path=None):
        """
        Initialize YOLOv8 model.
        Auto-downloads 'yolov8n.pt' if not present.
        """
        if model_path is None:
            model_path = config.MODEL_PATH
        self.model = YOLO(model_path)
    
    def process_frame(self, frame):
        """
        Detect objects in a frame.
        Returns:
            - processed_frame (with bounding boxes)
            - detections (list of dicts: {label, conf, box})
            - timestamp
        """
        results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
        
        detections = []
        
        # We generally work with the first result in the list (single frame)
        result = results[0]
        
        # Extract detections
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = self.model.names[class_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist() # Coordinates
            
            detections.append({
                "label": label,
                "confidence": round(conf, 2),
                "box": xyxy
            })

        # Draw bounding boxes
        annotated_frame = result.plot()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add timestamp to frame
        cv2.putText(annotated_frame, timestamp, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated_frame, detections, timestamp

if __name__ == "__main__":
    # Test with webcam
    cap = cv2.VideoCapture(0)
    vision = VisionEngine()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        ann_frame, dets, ts = vision.process_frame(frame)
        cv2.imshow("Vision Test", ann_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
