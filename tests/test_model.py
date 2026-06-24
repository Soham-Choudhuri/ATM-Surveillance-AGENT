import sys
import os
from PIL import Image, ImageDraw
import json

# Setup path for internal imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import IncidentAgent

def test_local_model():
    print("--- Local AI Model Test (Moondream/Ollama) ---")
    
    # 1. Initialize Agent
    try:
        agent = IncidentAgent()
        print(f"[INFO] Initialized IncidentAgent with model: {agent.model_name}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize agent: {e}")
        return

    # 2. Create a dummy test image if no image provided
    # Let's create a 640x480 image with a "person-like" rectangle for simulation
    test_img = Image.new('RGB', (640, 480), color=(30, 30, 30))
    draw = ImageDraw.Draw(test_img)
    draw.rectangle([200, 100, 400, 400], fill=(100, 100, 255)) # Simulate a 'person'
    
    # 3. Simulate YOLO Detections
    mock_detections = [
        {"label": "person", "confidence": 0.85, "box": [200, 100, 400, 400]}
    ]
    location = "ATM Vestibule"

    print(f"[INFO] Running reasoning on mock {location} scene...")
    
    # 4. Run Analysis
    try:
        report = agent.analyze_incident(test_img, mock_detections, location)
        print("\n--- AI Intelligence Report ---")
        print(json.dumps(report, indent=4))
        
        if report.get("classification") == "Error":
             print("\n[!] WARNING: The agent returned an error. Ensure Ollama is running and the model is pulled.")
        else:
             print("\n[SUCCESS] Local AI model responded correctly.")
             
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Script execution failed: {e}")
        print("Tip: Make sure you have run 'ollama pull moondream' and the Ollama server is running.")

if __name__ == "__main__":
    test_local_model()
