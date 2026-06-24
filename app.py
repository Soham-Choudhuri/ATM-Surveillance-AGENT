import streamlit as st
import cv2
import tempfile
import time
import os
import json
from PIL import Image
import numpy as np
import pandas as pd # For history table

# Custom Modules
import config
from core.vision import VisionEngine
from core.agent import IncidentAgent
from core.decision import evaluate_threat
from comms import alerts

# --- Page Setup ---
st.set_page_config(
    page_title="Multimodal AI Surveillance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for "Premium" Look ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
    }
    div[data-testid="metric-container"] {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ff4b4b;
    }
    .report-text {
        font-family: 'Courier New', monospace;
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #444;
        max-height: 200px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = 0
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # Input Source
    input_source = st.radio("Select Input Source:", ("Webcam", "Upload Video"))
    
    video_file = None
    if input_source == "Upload Video":
        video_file = st.file_uploader("Upload Surveillance Footage", type=['mp4', 'avi', 'mov'])
    
    # Start/Stop Buttons
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("▶ START", use_container_width=True)
    with col2:
        stop_btn = st.button("⏹ STOP", use_container_width=True)
        
    if start_btn:
        st.session_state.monitoring = True
    if stop_btn:
        st.session_state.monitoring = False

    st.markdown("---")
    if st.button("📨 Send Test WhatsApp Alert"):
        with st.spinner("Sending test message..."):
            result = alerts.send_alert("🚨 TEST: Manual alert from Surveillance Dashboard.")
            if result:
                st.success("Test Message Sent! Check your WhatsApp.")
            else:
                st.error("Test Failed. Check terminal logs.")

    st.markdown("---")
    st.info("System Status: " + ("🟢 Online" if st.session_state.monitoring else "🔴 Offline"))

    # Display active VLM configuration
    try:
        with open("model_config.json", "r") as f:
            mcfg = json.load(f)
        active_prov = mcfg.get("provider", "ollama").title()
        active_mod = mcfg.get("model_name", "moondream")
        st.caption(f"🧠 Active VLM: {active_prov} ({active_mod})")
    except:
        st.caption("🧠 Active VLM: Local (Moondream)")

    if os.path.exists(".admin_access"):
        st.markdown("---")
        st.markdown("🔒 **[Open Admin Portal](http://localhost:8502)**")


# --- Main Layout ---
col_video, col_intel = st.columns([2, 1])

# Initialize Engines
vision_model = VisionEngine()
agent = IncidentAgent()

# Placeholders
with col_video:
    st.subheader("🎥 Live Feed")
    frame_placeholder = st.empty()

with col_intel:
    st.subheader("🧠 Intelligence Hub")
    
    # Metrics
    m1, m2 = st.columns(2)
    with m1:
        threat_level_display = st.empty()
        threat_level_display.metric(label="Threat Level", value="Waiting...")
    with m2:
        obj_count_display = st.empty()
        obj_count_display.metric(label="Objects", value="0")
        
    st.markdown("### 📋 AI Incident Report")
    report_area = st.empty()
    action_area = st.empty()

# --- Main Processing Loop ---
if st.session_state.monitoring:
    
    # Setup Video Capture
    cap = None
    tfile = None
    if input_source == "Webcam":
        cap = cv2.VideoCapture(0)
    elif video_file:
        suffix = os.path.splitext(video_file.name)[1]
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix) 
        tfile.write(video_file.read())
        tfile.close() # CRITICAL: Release Python file lock before passing to cv2
        cap = cv2.VideoCapture(tfile.name)
    
    if cap and cap.isOpened():
        
        frame_count = 0
        last_analysis = 0
        # analysis_interval = 2.0 # Old value - leading to quota issues
        
        # Get interval from sidebar (default 10s to save quota)
        analysis_interval = st.sidebar.slider("⏱️ AI Analysis Interval (sec)", min_value=2.0, max_value=60.0, value=10.0)
        
        # Initial status
        threat_level_display.metric(label="Threat Level", value="LOW", delta_color="normal")
        report_area.markdown(f"Waiting for activity...", unsafe_allow_html=True)
        
        while cap.isOpened() and st.session_state.monitoring:
            ret, frame = cap.read()
            if not ret:
                st.warning("Video stream ended.")
                st.session_state.monitoring = False
                break
            
            # Webhook state check (poll every 10 frames to avoid excessive IO)
            if frame_count % 10 == 0:
                if os.path.exists("status.json"):
                    try:
                        with open("status.json", "r") as f:
                            status_data = json.load(f)
                        if not status_data.get("monitoring", True):
                            st.warning("Monitoring stopped remotely via Webhook.")
                            st.session_state.monitoring = False
                            # Reset status.json so it doesn't immediately stop again on restart
                            with open("status.json", "w") as f:
                                json.dump({"monitoring": True}, f)
                            break
                    except Exception:
                        pass
            
            frame_count += 1
            # Apply Frame Skip to reduce load
            if frame_count % config.Frame_Skip != 0:
                continue
            
            # 1. Vision Processing (Every Nth Frame)
            annotated_frame, detections, timestamp = vision_model.process_frame(frame)
            
            # Display Video
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            obj_count = len(detections)
            obj_count_display.metric(label="Objects Detected", value=str(obj_count))

            # 2. AI Agent Reasoning (Throttled)
            current_time = time.time()
            if (current_time - last_analysis > analysis_interval) and obj_count > 0:
                
                # Convert frame for Local AI Reasoning Agent (Ollama)
                pil_image = Image.fromarray(frame_rgb)
                
                # Call Agent
                with st.spinner("🤖 AI Reasoning..."):
                    incident_report = agent.analyze_incident(pil_image, detections)
                last_analysis = current_time
                
                # 3. Decision Engine
                action_log, requires_alert, alert_msg = evaluate_threat(incident_report)
                
                # Update UI
                severity = incident_report.get("severity", "Low").upper()
                delta_color = "inverse" if severity == "HIGH" else "normal"
                threat_level_display.metric(label="Threat Level", value=severity, delta=incident_report.get("classification"), delta_color=delta_color)
                
                formatted_report = f"""
                <div class="report-text">
                <b>Time:</b> {timestamp}<br>
                <b>Classification:</b> {incident_report.get('classification')}<br>
                <b>Summary:</b> {incident_report.get('description')}<br>
                <b>Recommendation:</b> {incident_report.get('recommendation')}
                </div>
                """
                report_area.markdown(formatted_report, unsafe_allow_html=True)
                
                if severity == "HIGH":
                    action_area.error(f"ACTION: {action_log}")
                else:
                    action_area.success(f"Action: {action_log}")
                
                # 4. Alerting System (Twilio)
                if requires_alert and (current_time - st.session_state.last_alert_time > 60):
                    with st.spinner("🚨 Sending WhatsApp Alert..."):
                         success = alerts.send_alert(alert_msg)
                         if success:
                             st.toast("WhatsApp Alert Sent to Authorities!", icon="✅")
                             st.session_state.last_alert_time = current_time
                             
                             # Log to history
                             st.session_state.history.append({
                                 "Time": timestamp,
                                 "Location": "Auto-Inferred",
                                 "Severity": severity,
                                 "Alert Sent": "Yes"
                             })
                         else:
                             st.error("❌ Alert Failed! Check Twilio config or logs.")
                             st.session_state.history.append({
                                 "Time": timestamp,
                                 "Location": "Auto-Inferred",
                                 "Severity": severity,
                                 "Alert Sent": "Failed"
                             })
                
                # Log non-alerts to history if suspicious
                elif severity in ["MEDIUM", "HIGH"]:
                     st.session_state.history.append({
                         "Time": timestamp,
                         "Location": "Auto-Inferred",
                         "Severity": severity,
                         "Alert Sent": "No (Throttled/Logged)"
                     })

            # Simple FPS limiter if needed, but Streamlit is already slow enough
            time.sleep(0.01) 
            
        cap.release()
        
        # Clean up temporary video file if it was created
        if tfile and os.path.exists(tfile.name):
            try:
                os.remove(tfile.name)
            except Exception as e:
                st.error(f"Failed to clean up temporary video file: {e}")

# --- Incident History ---
st.markdown("### 📜 Incident History Log")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.table(df)
else:
    st.info("No incidents recorded yet.")
