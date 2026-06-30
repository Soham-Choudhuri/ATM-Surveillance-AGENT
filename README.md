# AwareX: Multimodal Autonomous Surveillance System

AwareX is a next-generation, deeply autonomous AI surveillance system. Unlike traditional closed-circuit systems that rely on human operators to constantly stare at screens, AwareX utilizes **Multimodal Artificial Intelligence** (combining Computer Vision and Large Language Models) to autonomously detect, reason about, and report security threats in real-time.

It acts as a tireless, expert security analyst that actively watches camera feeds, listens to audio anomalies, and immediately pages human authorities via WhatsApp or SMS the moment an emergency occurs.

See **[Changelog](docs/Changelog.md)** for recent architectural changes, new features, additions and fixes and improvements added to the project.

## Key Features

### Advanced Multimodal Intelligence
- **Vision Engine**: Leverages blazing-fast **YOLOv8** object tracking to monitor physical movement.
- **Visual Reasoning**: Instead of just drawing bounding boxes, the system passes critical frames to a Vision Language Model (like **Moondream**, **Gemini**, or **Llama 3.2 Vision**) to contextualize the scene and evaluate actual threat levels (e.g., distinguishing between a technician fixing an ATM and a vandal tampering with it).
- **Audio Monitoring**: AwareX listens. If it detects loud anomalies (like breaking glass or screaming), it injects that context directly into the AI's reasoning pipeline.

### Dynamic Camera Management
- Connect any standard USB Webcam or external **RTSP / HTTP IP Camera**.
- Features a zero-code **Camera Management UI** powered by SQLite, allowing operators to instantly add, test, or delete surveillance streams on the fly.

### Central Dispatch & Automated Alerting
- **Central Dispatch Portal**: A highly responsive, dedicated view (`/dispatch`) designed for a secondary monitor or mobile device. When a CRITICAL incident is detected, it pulses a massive alert that requires manual operator acknowledgment.
- **Two-Way Communications**: Pushes detailed incident reports, confidence scores, and action recommendations directly to your phone via Twilio (SMS/WhatsApp). 
- **Remote Stopping**: Reply to the alert message with `"Stop"` from your phone, and AwareX will automatically halt the live feed and AI processing.

### Historical Incident Database
- All analysis logs are permanently saved to a local **SQLite Database**.
- View, search, and manage historical threats securely via the passwordless Admin Logs portal.

## Quick Start

1. Ensure you have the required portable toolchains (Python, Node.js, Ollama) installed and configured on your host machine.
2. Clone the repository and execute the unified launch script:
   ```cmd
   run.bat
   ```
3. The script will automatically start the Ollama Engine, launch the FastAPI Python backend, compile the Next.js frontend, and open a terminal for you.
4. Navigate to `http://localhost:3000` to view the dashboard!

## Documentation & Guides
- **[Remote Access & VPN Guide](docs/tailscale_setup_guide.md)**: Learn how to set up Tailscale to securely access your AwareX dashboard and video feeds from anywhere in the world, completely bypassing Windows Firewall limitations.
- **[Twilio Alerting Setup Guide](docs/twilio_free_setup_guide.md)**: A step-by-step walkthrough for configuring the free Twilio SMS and WhatsApp integration to receive autonomous alerts.