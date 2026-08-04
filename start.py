#!/usr/bin/env python3
"""
NeoBank Support Chatbot — Start script (Python)
Starts all services and opens browser for testing.
Cross-platform: works on Linux, macOS, Windows.
"""

import contextlib
import os
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

# Configuration
PROJECT_DIR = Path(__file__).parent
AGENT_API_PORT = 8000
STREAMLIT_PORT = 8501


# ANSI colors
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def print_header():
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}  🏦 NeoBank Support Chatbot — Startup{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()


def print_status(msg: str, status: str = "info"):
    icons = {
        "ok": f"{Colors.GREEN}✓{Colors.NC}",
        "warn": f"{Colors.YELLOW}⚠{Colors.NC}",
        "error": f"{Colors.RED}✗{Colors.NC}",
        "info": f"{Colors.BLUE}→{Colors.NC}",
    }
    print(f"  {icons.get(status, ' ')} {msg}")


def check_dependencies():
    print(f"{Colors.YELLOW}[1/6] Checking dependencies...{Colors.NC}")

    # Check Python version
    # Runtime guard for users on an older interpreter — ruff flags it as dead under
    # target-version py312, but this script is the entry point people run before any venv exists.
    if sys.version_info < (3, 12):  # noqa: UP036
        print_status(f"Python {sys.version} (need 3.12+)", "error")
        sys.exit(1)
    print_status(f"Python {sys.version.split()[0]}", "ok")

    # Check if venv exists
    venv_dir = PROJECT_DIR / ".venv"
    if not venv_dir.exists():
        print_status("Creating virtual environment...", "info")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Get venv Python
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    # Install dependencies if needed
    try:
        import fastapi  # noqa: F401  (availability probe)
    except ImportError:
        print_status("Installing dependencies...", "info")
        subprocess.run(
            [
                str(venv_python),
                "-m",
                "pip",
                "install",
                "-q",
                "fastapi",
                "uvicorn[standard]",
                "sse-starlette",
                "pydantic",
                "pydantic-settings",
                "httpx",
                "structlog",
                "python-dotenv",
                "sqlalchemy[asyncio]",
                "asyncpg",
                "redis",
                "prometheus-client",
                "langchain-core",
                "langgraph",
                "litellm",
                "pytest",
                "pytest-asyncio",
                "streamlit",
            ],
            check=True,
            capture_output=True,
        )

    print_status("Dependencies ready", "ok")
    print()
    return venv_python


def check_services():
    print(f"{Colors.YELLOW}[2/6] Checking services...{Colors.NC}")

    services_ok = True

    # Check PostgreSQL
    try:
        import asyncio

        import asyncpg

        asyncio.run(asyncpg.connect("postgresql://neobank:neobank_secret@localhost:5432/neobank"))
        print_status("PostgreSQL running", "ok")
    except Exception:
        print_status("PostgreSQL not running (will use mock data)", "warn")
        services_ok = False

    # Check Redis
    try:
        import redis

        r = redis.Redis()
        r.ping()
        print_status("Redis running", "ok")
    except Exception:
        print_status("Redis not running (queue features limited)", "warn")

    # Check ChromaDB
    try:
        req = urllib.request.Request("http://localhost:8001/api/v1/heartbeat")
        urllib.request.urlopen(req, timeout=2)
        print_status("ChromaDB running", "ok")
    except Exception:
        print_status("ChromaDB not running (RAG features limited)", "warn")

    print()
    return services_ok


def init_database():
    print(f"{Colors.YELLOW}[3/6] Initializing database...{Colors.NC}")

    try:
        import asyncio

        import asyncpg

        async def run_init():
            try:
                conn = await asyncpg.connect(
                    "postgresql://neobank:neobank_secret@localhost:5432/neobank"
                )

                # Run schema
                init_sql = PROJECT_DIR / "ops" / "init.sql"
                if init_sql.exists():
                    sql = init_sql.read_text()
                    for stmt in sql.split(";"):
                        stmt = stmt.strip()
                        if stmt and not stmt.startswith("--"):
                            try:
                                await conn.execute(stmt)
                            except Exception as e:
                                if "already exists" not in str(e):
                                    pass

                # Run seeds
                seed_sql = PROJECT_DIR / "data" / "seeds" / "customers.sql"
                if seed_sql.exists():
                    sql = seed_sql.read_text()
                    for stmt in sql.split(";"):
                        stmt = stmt.strip()
                        if stmt and not stmt.startswith("--"):
                            with contextlib.suppress(Exception):
                                await conn.execute(stmt)

                await conn.close()
                return True
            except Exception as e:
                print(f"  Database init error: {e}")
                return False

        result = asyncio.run(run_init())
        if result:
            print_status("Database initialized", "ok")
        else:
            print_status("Database init skipped", "warn")
    except Exception:
        print_status("Database init skipped (asyncpg not available)", "warn")

    print()


def kill_existing_processes():
    print(f"{Colors.YELLOW}[4/6] Cleaning up existing processes...{Colors.NC}")

    for port in [AGENT_API_PORT, STREAMLIT_PORT]:
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True
                )
                for line in result.stdout.split("\n"):
                    if f":{port}" in line and "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
            else:
                result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
                for pid in result.stdout.strip().split("\n"):
                    if pid:
                        subprocess.run(["kill", "-9", pid], capture_output=True)
        except Exception:
            pass

    print_status("Cleanup done", "ok")
    print()


def start_agent_api(python_path: Path) -> subprocess.Popen:
    print(f"{Colors.YELLOW}[5/6] Starting Agent API (port {AGENT_API_PORT})...{Colors.NC}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_DIR)
    env["LLM_PROVIDER"] = env.get("LLM_PROVIDER", "ollama")

    if sys.platform == "win32":
        proc = subprocess.Popen(
            [
                str(python_path),
                "-m",
                "uvicorn",
                "services.agent_api.interface.app:create_app",
                "--factory",
                "--host",
                "0.0.0.0",
                "--port",
                str(AGENT_API_PORT),
                "--reload",
                "--log-level",
                "info",
            ],
            cwd=str(PROJECT_DIR),
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        proc = subprocess.Popen(
            [
                str(python_path),
                "-m",
                "uvicorn",
                "services.agent_api.interface.app:create_app",
                "--factory",
                "--host",
                "0.0.0.0",
                "--port",
                str(AGENT_API_PORT),
                "--reload",
                "--log-level",
                "info",
            ],
            cwd=str(PROJECT_DIR),
            env=env,
            preexec_fn=os.setsid,
        )

    # Wait for API to be ready
    print("  Waiting for API to start...")
    for _ in range(30):
        try:
            req = urllib.request.Request("http://localhost:8000/health")
            urllib.request.urlopen(req, timeout=2)
            print_status("Agent API ready", "ok")
            print()
            return proc
        except Exception:
            time.sleep(1)

    print_status("Agent API started (may still be loading)", "warn")
    print()
    return proc


def start_streamlit(python_path: Path) -> subprocess.Popen:
    print(f"{Colors.YELLOW}[6/6] Starting Streamlit (port {STREAMLIT_PORT})...{Colors.NC}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_DIR)

    frontend = PROJECT_DIR / "frontend" / "app.py"

    if sys.platform == "win32":
        proc = subprocess.Popen(
            [
                str(python_path),
                "-m",
                "streamlit",
                "run",
                str(frontend),
                "--server.port",
                str(STREAMLIT_PORT),
                "--server.headless",
                "true",
                "--browser.gatherUsageStats",
                "false",
            ],
            cwd=str(PROJECT_DIR),
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        proc = subprocess.Popen(
            [
                str(python_path),
                "-m",
                "streamlit",
                "run",
                str(frontend),
                "--server.port",
                str(STREAMLIT_PORT),
                "--server.headless",
                "true",
                "--browser.gatherUsageStats",
                "false",
            ],
            cwd=str(PROJECT_DIR),
            env=env,
            preexec_fn=os.setsid,
        )

    # Wait for Streamlit
    print("  Waiting for Streamlit...")
    for _ in range(20):
        try:
            req = urllib.request.Request(f"http://localhost:{STREAMLIT_PORT}")
            urllib.request.urlopen(req, timeout=2)
            print_status("Streamlit ready", "ok")
            print()
            return proc
        except Exception:
            time.sleep(1)

    print_status("Streamlit started", "ok")
    print()
    return proc


def open_browser():
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.GREEN}🚀 All services started!{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"  {Colors.GREEN}Agent API:{Colors.NC}      http://localhost:{AGENT_API_PORT}")
    print(f"  {Colors.GREEN}Streamlit UI:{Colors.NC}   http://localhost:{STREAMLIT_PORT}")
    print(f"  {Colors.GREEN}API Docs:{Colors.NC}       http://localhost:{AGENT_API_PORT}/docs")
    print(f"  {Colors.GREEN}Health:{Colors.NC}         http://localhost:{AGENT_API_PORT}/health")
    print()

    # Open browser
    try:
        webbrowser.open(f"http://localhost:{STREAMLIT_PORT}")
        print_status("Browser opened", "ok")
    except Exception:
        print_status(f"Please open http://localhost:{STREAMLIT_PORT} in your browser", "warn")

    print()


def main():
    print_header()

    # Check dependencies
    venv_python = check_dependencies()

    # Check services
    check_services()

    # Init database
    init_database()

    # Cleanup
    kill_existing_processes()

    # Start services
    agent_proc = start_agent_api(venv_python)
    streamlit_proc = start_streamlit(venv_python)

    # Open browser
    open_browser()

    # Handle shutdown
    def signal_handler(sig, frame):
        print()
        print(f"{Colors.YELLOW}Stopping services...{Colors.NC}")
        for proc in [agent_proc, streamlit_proc]:
            if proc and proc.poll() is None:
                if sys.platform == "win32":
                    proc.terminate()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print(f"{Colors.GREEN}✓ All services stopped{Colors.NC}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"{Colors.YELLOW}Press Ctrl+C to stop all services{Colors.NC}")
    print()

    # Wait for any process
    try:
        while True:
            if agent_proc.poll() is not None:
                print_status("Agent API stopped", "warn")
                break
            if streamlit_proc.poll() is not None:
                print_status("Streamlit stopped", "warn")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    signal_handler(None, None)


if __name__ == "__main__":
    main()
