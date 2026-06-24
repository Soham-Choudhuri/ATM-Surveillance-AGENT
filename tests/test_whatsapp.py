import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comms import alerts
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("--- WhatsApp Alert Test ---")
print("This script will attempt to send a test message to your configured WhatsApp number.")
print("Ensure you have joined the Twilio Sandbox by sending 'join <keyword>' to the Twilio number.")

confirmation = input("Type 'yes' to proceed: ")

if confirmation.lower() == 'yes':
    print("Sending...")
    success = alerts.send_alert("🚨 TEST: This is a verification message from your AI Surveillance Project.")
    
    if success:
        print("\n✅ SUCCESS: Check your WhatsApp now!")
    else:
        print("\n❌ FAILED: Check the error logs above.")
else:
    print("Test cancelled.")
