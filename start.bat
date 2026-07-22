@echo off
REM NeoBank Support Chatbot — Start script (Windows)
REM Starts all services and opens browser for testing

echo ═══════════════════════════════════════════════════
echo   🏦 NeoBank Support Chatbot — Startup
echo ═══════════════════════════════════════════════════
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.12+.
    pause
    exit /b 1
)
echo ✓ Python found

REM Create venv if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -q fastapi uvicorn[standard] sse-starlette pydantic pydantic-settings httpx structlog python-dotenv sqlalchemy asyncpg redis prometheus-client langchain-core langgraph litellm pytest pytest-asyncio streamlit 2>nul
)

echo ✓ Dependencies ready
echo.

REM Set environment variables
set PYTHONPATH=%CD%
set LLM_PROVIDER=ollama

REM Start Agent API
echo [1/3] Starting Agent API (port 8000)...
start "NeoBank Agent API" cmd /c "cd /d %CD% && .venv\Scripts\activate.bat && python -m uvicorn services.agent_api.interface.app:create_app --factory --host 0.0.0.0 --port 8000 --reload --log-level info"

REM Wait for API
timeout /t 5 /nobreak >nul

REM Start Streamlit
echo [2/3] Starting Streamlit (port 8501)...
start "NeoBank Streamlit" cmd /c "cd /d %CD% && .venv\Scripts\activate.bat && streamlit run frontend/app.py --server.port 8501 --server.headless true"

REM Wait for Streamlit
timeout /t 5 /nobreak >nul

echo [3/3] Opening browser...
echo.
echo ═══════════════════════════════════════════════════
echo   🚀 Services started!
echo ═══════════════════════════════════════════════════
echo.
echo   Agent API:      http://localhost:8000
echo   Streamlit UI:   http://localhost:8501
echo   API Docs:       http://localhost:8000/docs
echo.

start http://localhost:8501

echo Press any key to stop services...
pause >nul

REM Kill processes
taskkill /FI "WINDOWTITLE eq NeoBank Agent API" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq NeoBank Streamlit" /F >nul 2>&1
echo ✓ Services stopped
