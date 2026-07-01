import ollama
import config
from PIL import Image
import json
import logging
import io
import re
import os
import base64
import requests

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "model_config.json"

class IncidentAgent:
    def __init__(self):
        pass # Configuration is loaded dynamically per request to allow hot-swapping
        
    def _load_config(self):
        default_config = {
            "active_mode": "local",
            "provider": "ollama",
            "model_name": config.LOCAL_LLM_MODEL,
            "api_key": ""
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                return default_config
        return default_config

    def analyze_incident(self, image_input, detections, context_str=""):
        cfg = self._load_config()
        active_mode = cfg.get("active_mode", "local")
        provider = cfg.get("provider", "ollama")
        model_name = cfg.get("model_name", config.LOCAL_LLM_MODEL)
        api_key = cfg.get("api_key", "")
        
        prompt = f"""
Act as an expert Security Analyst. You are monitoring a live surveillance feed.
I will provide you with an image and a list of objects detected by a YOLO model: {detections}.
{f"CRITICAL SYSTEM ALERTS TO CONSIDER:\\n{context_str}" if context_str else ""}

TASK:
Analyze the image carefully. Identify any suspicious activity, safety threats, or unusual behavior based on the visual context and any provided system alerts.

OUTPUT REQUIREMENTS:
You MUST respond with a raw JSON object and nothing else.
DO NOT output the literal placeholder text. You must generate your own realistic analysis based on the image.
Use the following exact keys:
- "classification": Choose one of ["Normal", "Suspicious", "Critical"]
- "severity": Choose one of ["Low", "Medium", "High"]
- "confidence_score": Provide a number between 0 and 100 representing your confidence in this assessment.
- "description": Write a 2-3 sentence descriptive summary of the scene.
- "recommendation": Write a specific, actionable recommendation for security personnel.

EXAMPLE VALID RESPONSE:
{{
    "classification": "Suspicious",
    "severity": "Medium",
    "confidence_score": 85,
    "description": "A person is loitering near the ATM machine for an extended period without initiating a transaction.",
    "recommendation": "Dispatch a guard to check on the individual and ensure the area is secure."
}}
"""

        try:
            if active_mode == "local" or provider == "ollama":
                response_text = self._call_ollama(image_input, prompt, model_name)
            elif provider == "gemini":
                response_text = self._call_gemini(image_input, prompt, model_name, api_key)
            elif provider == "groq":
                response_text = self._call_groq(image_input, prompt, model_name, api_key)
            elif provider == "huggingface":
                response_text = self._call_huggingface(image_input, prompt, model_name, api_key)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
            return self._parse_json(response_text)
            
        except Exception as e:
            logger.error(f"VLM Analysis Failed ({provider}): {e}")
            return {
                "classification": "Error",
                "severity": "Low",
                "confidence_score": 0,
                "description": f"Analysis failed: {str(e)}",
                "recommendation": f"Check {provider} configuration and API keys."
            }



    def _parse_json(self, text_response):
        text_response = text_response.strip()
        # Clean markdown if present
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "", 1)
        if text_response.endswith("```"):
            text_response = text_response[:text_response.rfind("```")]
            
        try:
            return json.loads(text_response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            raise ValueError("Could not parse valid JSON from model response.")

    def _call_ollama(self, img, prompt, model_name):
        client = ollama.Client(host=config.OLLAMA_HOST)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        response = client.generate(
            model=model_name,
            prompt=prompt,
            images=[img_bytes],
            format='json',
            stream=False
        )
        return response.get('response', '')

    def _call_gemini(self, img, prompt, model_name, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, img])
        return response.text

    def _call_groq(self, img, prompt, model_name, api_key):
        from groq import Groq
        client = Groq(api_key=api_key)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=model_name,
        )
        return chat_completion.choices[0].message.content

    def _call_huggingface(self, img, prompt, model_name, api_key):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
