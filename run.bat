@echo off
setlocal

rem 1. Inject Portable Dev Environment tools into this session's memory
set PATH=C:\System\Dev\Ollama;C:\System\Dev\Python313;C:\System\Dev\Node;C:\System\Dev\Node\npm-global;%PATH%

rem 2. Configure Portable Ollama Variables
set OLLAMA_MODELS=C:\System\Dev\Ollama\models
set OLLAMA_VULKAN=1

rem Define virtual environment folder name
set VENV_DIR=venv

rem Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] No virtual environment found. Creating one now...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
)

rem Activate the virtual environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

rem Install requirements
echo [INFO] Checking and installing requirements from requirements.txt...
pip install -r requirements.txt

rem Run the Unified Application
echo.
echo =======================================================
echo [INFO] Starting the AI Surveillance System...
echo [INFO] Launching FastAPI Backend (Port 8000)...
echo [INFO] Launching Next.js Frontend (Port 3000)...
echo [INFO] Launching Ollama AI Engine (Port 11434)...
echo [INFO] Opening Portable Interactive Console...
echo =======================================================
echo.

rem Launch all three servers in their own dedicated windows
start "AI Surveillance - Ollama Engine" cmd /k "ollama serve"
start "AI Surveillance - Backend API" cmd /k "call %VENV_DIR%\Scripts\activate.bat && uvicorn backend.main:app --host 0.0.0.0 --port 8000"
start "AI Surveillance - Web UI" cmd /k "cd frontend && npm run dev"

rem Launch a fourth window that remains open and empty for your own manual commands
start "AI Surveillance - Interactive Console" cmd /k "echo [READY] This terminal is initialized with your portable toolchain. You can run manual commands here."

echo [INFO] All services and an interactive console have been launched.
exit