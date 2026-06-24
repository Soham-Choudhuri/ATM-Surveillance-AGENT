# Multimodal Autonomous AI Surveillance System 🛡️

## 🎓 Final Year Engineering Project Prototype

An end-to-end AI surveillance system that uses **Computer Vision (YOLOv8)** for object detection and a **Local Multimodal AI Agent (Moondream via Ollama)** to reason about threats and autonomously alert authorities via **WhatsApp (Twilio)**.

---

## 🚀 Features

*   **Real-time Monitoring**: Webcam or Video Upload.
*   **Vision Intelligence**: Detects people, bags, vehicles, etc.
*   **AI Reasoning Agent**: Understands context (e.g., "Person lying down in ATM" is dangerous).
*   **Autonomous Decisions**: Classifies threats as Low/Medium/High.
*   **Instant WhatsApp Alerts**: Sends real-time alerts to authorities for CRITICAL threats.
*   **Two-Way Communication**: Authorities can reply "Status" or "Ack" to interact with the system.
*   **Live Dashboard**: Professional UI built with Streamlit.

---

## 🛠️ Technology Stack

*   **Language**: Python 3.10+
*   **Computer Vision**: YOLOv8, OpenCV
*   **LLM / AI Agent**: Local Moondream (via Ollama VLM)
*   **Alerts & Webhooks**: Twilio API (WhatsApp)
*   **Backend / Webhook**: FastAPI + Uvicorn
*   **Tunneling**: Ngrok
*   **Frontend**: Streamlit

---

## 📂 Project Structure

```
/ai_surveillance/
 ├── core/               # Core Logic (Vision, Agent, Decision)
 ├── comms/              # Communication (Alerts, Webhooks)
 ├── models/             # ML Model Weights (YOLO)
 ├── docs/               # Documentation
 ├── tests/              # Test Scripts
 ├── app.py              # Main Dashboard Application
 ├── config.py           # Configuration
 └── requirements.txt    # Dependencies
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
Ensure you have Python installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your API keys:

```ini
# No Google API Key required for Local AI
# Keep your Twilio Credentials below

# Twilio Credentials
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=whatsapp:+14155238886
AUTHORITY_PHONE_NUMBER=whatsapp:+91xxxxxxxxxx
```

### 4. Run the Dashboard ( Surveillance System )
```bash
streamlit run app.py
```

---

## 📡 Enable Two-Way Communication (Optional)

To allow authorities to **reply** to alerts, follow these steps:

### 1. Start the Webhook Server
Open a **new terminal** and run:
```bash
python webhook_server.py
```

### 2. Expose the Server via Ngrok
Run this command to make your local server accessible to Twilio:
```bash
ngrok http 8000
```
*Copy the URL (e.g., `https://xxxx.ngrok-free.app`).*

### 3. Configure Twilio
*   Go to **Twilio Console > Messaging > Settings > WhatsApp Sandbox Settings**.
*   In **"When a message comes in"**, paste your URL + `/whatsapp-webhook`.
*   Example: `https://xxxx.ngrok-free.app/whatsapp-webhook`
*   Set Method to **POST**.
*   Save.

### 4. Test Commands
You can now reply to the WhatsApp bot with:
*   `Status`: Checks if system is online.
*   `Ack`: Acknowledge an alert.

---

## 🧪 How to Demo

1.  **Start the App**: `streamlit run app.py`
2.  **Select Source**: Choose "Webcam".
3.  **Click START**: Monitoring begins.
4.  **Simulate Threat**:
    *   Create a scenario (e.g., abandon a bag).
    *   **Vision Layer** detects object.
    *   **AI Agent** classifies it as Critical.
    *   **Phone Buzzes**: You receive a WhatsApp alert.
5.  **Interactive Reply**:
    *   Reply "Status" on WhatsApp.
    *   System replies "🟢 System is ONLINE...".

---

## 🧠 System Architecture

```
[ Camera Feed ] --> [ YOLOv8 Detection ] --> [ Local AI Agent (Ollama + Moondream) ]
                                                      |
                                              [ Decision Engine ]
                                                      |
                                          -------------------------
                                          |                       |
                                     [ Dashboard ]       [ Twilio WhatsApp ]
                                                                  |
                                                                  v
                                                         (Authority Replies)
                                                                  |
                                                        [ Ngrok + FastAPI ]
```

---

**Note**: For the evaluation/Viva, ensure you have a valid Internet connection.
