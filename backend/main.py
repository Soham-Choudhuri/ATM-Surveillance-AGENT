import sys
import os
import cv2
import json
import logging
import time
import tempfile
import base64
from datetime import datetime
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse

import config
from core.vision import VisionEngine
from core.agent import IncidentAgent
from core.decision import evaluate_threat
from comms.alerts import send_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
class AppState:
    def __init__(self):
        self.monitoring = False
        self.cap = None
        self.last_analysis_time = 0
        self.threat_level = "Waiting..."
        self.object_count = 0
        self.latest_report = None
        self.history = []
        self.is_analyzing = False
        self.analysis_interval = 10
        self.frame_reports = []

state = AppState()

# Initialize AI Modules
vision_engine = VisionEngine()
agent = IncidentAgent()

CONFIG_FILE = "model_config.json"
STATUS_FILE = "status.json"

@app.get("/api/state")
def get_state():
    return {
        "monitoring": state.monitoring,
        "threat_level": state.threat_level,
        "object_count": state.object_count,
        "latest_report": state.latest_report,
        "history": state.history,
        "is_analyzing": state.is_analyzing
    }

@app.post("/api/start")
def start_monitoring(source: str = Form(...), interval: int = Form(10), file: UploadFile = File(None)):
    if state.monitoring:
        return {"status": "Already monitoring"}
        
    state.input_source = source
    if source == "Upload Video" and file:
        suffix = os.path.splitext(file.filename)[1]
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tfile.write(file.file.read())
        tfile.close()
        state.video_path = tfile.name
        state.cap = cv2.VideoCapture(state.video_path)
    else:
        state.cap = cv2.VideoCapture(0)
        
    state.monitoring = True
    state.last_analysis_time = 0
    state.analysis_interval = interval
    state.frame_reports = []
    return {"status": "Started"}

@app.post("/api/stop")
def stop_monitoring():
    state.monitoring = False
    if state.cap:
        state.cap.release()
        state.cap = None
    state.threat_level = "Waiting..."
    state.latest_report = None
    state.object_count = 0
    return {"status": "Stopped"}

def generate_frames():
    frame_count = 0
    while True:
        if not state.monitoring or state.cap is None or not state.cap.isOpened():
            break
            
        success, frame = state.cap.read()
        if not success:
            if state.frame_reports:
                state.is_analyzing = True
                final_rep = agent.generate_final_report(state.frame_reports)
                state.is_analyzing = False
                state.history.insert(0, {
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Type": "Final Video Report",
                    "Severity": final_rep.get("severity", "LOW").upper(),
                    "Summary": final_rep.get("description", ""),
                    "Details": final_rep
                })
                state.frame_reports = []
            state.monitoring = False
            break

        frame_count += 1
        current_time = datetime.now().timestamp()
        
        # YOLO Processing with frame skipping
        if frame_count % config.Frame_Skip == 0:
            ann_frame, det_list, ts = vision_engine.process_frame(frame)
            frame = ann_frame # Use the annotated frame for the video feed
            
            detections = [d["label"] for d in det_list]
            state.object_count = len(detections)

            # AI Reasoning (every X seconds)
            if current_time - state.last_analysis_time > state.analysis_interval:
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                try:
                    state.is_analyzing = True
                    incident_report = agent.analyze_incident(pil_image, detections)
                    state.latest_report = incident_report
                    state.frame_reports.append(incident_report)
                    
                    # Decision Engine
                    severity = incident_report.get("severity", "LOW").upper()
                    classification = incident_report.get("classification", "Normal")
                    
                    # Update threat level string
                    state.threat_level = f"{severity} ({classification})"
                    
                    action_log, requires_alert, alert_msg = evaluate_threat(incident_report)
                    
                    if requires_alert:
                        send_alert(alert_msg)
                        
                except Exception as e:
                    logger.error(f"Error during incident analysis: {e}")
                finally:
                    state.is_analyzing = False
                
                # Update last_analysis_time to the time AFTER analysis finishes
                # This ensures exactly `interval` seconds of playback happen before the next analysis
                state.last_analysis_time = datetime.now().timestamp()

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)

@app.get("/api/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# Admin Config Endpoints
@app.get("/api/admin_check")
def admin_check():
    if os.path.exists(".admin_access"):
        return {"access": True}
    return {"access": False}

@app.get("/api/config")
def get_config():
    default_config = {
        "active_mode": "local",
        "provider": "ollama",
        "model_name": config.LOCAL_LLM_MODEL,
        "api_key": "",
        "twilio_sid": "",
        "twilio_auth": "",
        "twilio_type": "SMS",
        "twilio_from": "",
        "twilio_to": "",
        "alerts_enabled": False
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default_config
    return default_config

@app.post("/api/config")
async def save_config(request: Request):
    data = await request.json()
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return {"status": "Saved"}

# Webhook Endpoints
@app.post("/sms-webhook")
@app.post("/whatsapp-webhook")
async def inbound_reply(Body: str = Form(...), From: str = Form(...)):
    user_response = Body.lower().strip()
    resp = MessagingResponse()
    
    if "help" in user_response:
        reply_text = "Commands:\n- 'Status': Check system status\n- 'Stop': Stop alerts"
    elif "status" in user_response:
        reply_text = f"🟢 System is ONLINE. Monitoring: {state.monitoring}"
    elif "stop" in user_response:
        state.monitoring = False
        reply_text = "🛑 Stopping monitoring. Alerts suspended."
    else:
        reply_text = f"🤖 System received: '{Body}'. Type 'Help' for options."
        
    msg = resp.message()
    msg.body(reply_text)
    return str(resp)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        pass
