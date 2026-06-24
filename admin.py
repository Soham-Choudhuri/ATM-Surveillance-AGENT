import streamlit as st
import os
import json

st.set_page_config(page_title="System Administration", page_icon="🔐", layout="centered")

ADMIN_TOKEN_FILE = ".admin_access"
CONFIG_FILE = "model_config.json"

if not os.path.exists(ADMIN_TOKEN_FILE):
    st.error("Access Denied: Admin token file not found.")
    st.stop()

st.title("⚙️ System Administration")
st.subheader("Model Selection Routing")

# Default config
default_config = {
    "active_mode": "local",
    "provider": "ollama",
    "model_name": "moondream",
    "api_key": ""
}

# Load existing
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
        except:
            config = default_config
else:
    config = default_config

current_mode_index = 0 if config.get("active_mode") == "local" else 1
mode = st.radio("Select Processing Mode:", ("Local (Ollama)", "Cloud (API)"), index=current_mode_index)

# Map UI mode to JSON 'active_mode'
active_mode = "local" if "Local" in mode else "cloud"

provider = config.get("provider", "ollama")
model_name = config.get("model_name", "moondream")
api_key = config.get("api_key", "")

if active_mode == "local":
    st.info("Using local Ollama instance for inference. No API key required.")
    provider = "ollama"
    model_name = st.text_input("Ollama Model Name:", value=config.get("model_name", "moondream") if config.get("provider") == "ollama" else "moondream")

elif active_mode == "cloud":
    st.info("Using Cloud VLM API. Ensure you have the appropriate free tier API key.")
    
    # Provider Selection
    providers = ["Google Gemini", "Groq", "Hugging Face"]
    prov_map = {"gemini": 0, "groq": 1, "huggingface": 2}
    prov_idx = prov_map.get(config.get("provider"), 0) if config.get("active_mode") == "cloud" else 0
    provider_sel = st.selectbox("Cloud Provider:", providers, index=prov_idx)
    
    if provider_sel == "Google Gemini":
        provider = "gemini"
        models = ["gemini-1.5-flash", "gemini-1.5-pro"]
        mod_idx = models.index(config.get("model_name")) if config.get("model_name") in models and config.get("provider") == "gemini" else 0
        model_name = st.selectbox("Gemini Model:", models, index=mod_idx)
    elif provider_sel == "Groq":
        provider = "groq"
        models = ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]
        mod_idx = models.index(config.get("model_name")) if config.get("model_name") in models and config.get("provider") == "groq" else 0
        model_name = st.selectbox("Groq Vision Model:", models, index=mod_idx)
    elif provider_sel == "Hugging Face":
        provider = "huggingface"
        model_name = st.text_input("Hugging Face Model ID:", value=config.get("model_name", "llava-hf/llava-1.5-7b-hf") if config.get("provider") == "huggingface" else "llava-hf/llava-1.5-7b-hf")

    api_key = st.text_input(f"{provider_sel} API Key:", type="password", value=config.get("api_key", "") if config.get("provider") == provider else "")

if st.button("💾 Save Configuration"):
    new_config = {
        "active_mode": active_mode,
        "provider": provider,
        "model_name": model_name,
        "api_key": api_key
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(new_config, f, indent=4)
    st.success(f"Configuration saved! System will now use {provider} ({model_name}).")
