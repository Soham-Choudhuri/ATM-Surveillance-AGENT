from datetime import datetime
import time
from comms import alerts

def evaluate_threat(incident_report):
    """
    Decides the action based on the AI incident report.
    Returns:
        - action_log (str): Description of action taken.
        - requires_alert (bool): Whether an external alert (Twilio) is needed.
        - alert_message (str): Formatted message if alert is detecting.
    """
    severity = incident_report.get("severity", "Low").upper()
    classification = incident_report.get("classification", "INFO").upper()
    description = incident_report.get("description", "No description")
    recommendation = incident_report.get("recommendation", "No action")
    
    timestamp = datetime.now().strftime(f"%H:%M {time.tzname[0]}")
    
    # Dynamic Alert Message Formatting
    if severity == "HIGH" or classification == "CRITICAL":
        icon = "🚨"
        title = "CRITICAL SECURITY ALERT"
        action_log = "CRITICAL: Alerting Authorities"
    elif severity == "MEDIUM" or classification == "WARNING":
        icon = "⚠️"
        title = "WARNING: INCIDENT DETECTED"
        action_log = "WARNING: Incident Logged and Alerted"
    else:
        icon = "ℹ️"
        title = "INFO: ROUTINE MONITORING UPDATE"
        action_log = "INFO: Monitoring Update Sent"

    alert_msg = f"""
{icon} {title} {icon}

Location: [See Dashboard]
Time: {timestamp}
Detected Event: {description}
Severity: {severity}

AI Recommendation:
{recommendation}

— Autonomous AI Surveillance System
"""
    
    return action_log, True, alert_msg
