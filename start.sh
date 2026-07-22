#!/usr/bin/env bash
# NeoBank Support Chatbot — Start script
# Starts all services and opens browser for testing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# If shell.nix exists and nix is available, use nix-shell
if [ -f "shell.nix" ] && command -v nix-shell &>/dev/null; then
    echo "Using nix-shell for dependencies..."
    exec nix-shell --run "./start.sh"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🏦 NeoBank Support Chatbot — Startup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# --- Check dependencies ---
echo -e "${YELLOW}[1/7] Checking dependencies...${NC}"

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        echo -e "${RED}✗ $1 not found. Please install it.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
}

check_cmd python3
check_cmd pip

# Check if venv exists, create if not
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" &>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -q fastapi uvicorn[standard] sse-starlette pydantic pydantic-settings httpx structlog python-dotenv sqlalchemy asyncpg redis prometheus-client langchain-core langgraph litellm pytest pytest-asyncio streamlit 2>/dev/null
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# --- Check if required services are running ---
echo -e "${YELLOW}[2/7] Checking required services...${NC}"

# Set LD_LIBRARY_PATH for NixOS
export LD_LIBRARY_PATH="/nix/store/hngmi01i8wgi25a0byrxcn4ysz5j79mw-gcc-15.2.0-lib/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="$SCRIPT_DIR"

# Check PostgreSQL
if python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://neobank:neobank_secret@localhost:5432/neobank'))" &>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL running${NC}"
    PG_RUNNING=true
else
    echo -e "${YELLOW}⚠ PostgreSQL not running. Trying to start with Docker...${NC}"
    if command -v docker &>/dev/null; then
        docker run -d --name neobank-postgres \
            -e POSTGRES_USER=neobank \
            -e POSTGRES_PASSWORD=neobank_secret \
            -e POSTGRES_DB=neobank \
            -p 5432:5432 \
            postgres:16-alpine 2>/dev/null || true
        echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
        sleep 3
        PG_RUNNING=true
    else
        echo -e "${RED}✗ PostgreSQL not available and Docker not found${NC}"
        echo -e "${YELLOW}Please start PostgreSQL manually or install Docker${NC}"
        PG_RUNNING=false
    fi
fi

# Check Redis
if python -c "import redis; r = redis.Redis(); r.ping()" &>/dev/null; then
    echo -e "${GREEN}✓ Redis running${NC}"
    REDIS_RUNNING=true
else
    echo -e "${YELLOW}⚠ Redis not running. Trying to start with Docker...${NC}"
    if command -v docker &>/dev/null; then
        docker run -d --name neobank-redis \
            -p 6379:6379 \
            redis:7-alpine 2>/dev/null || true
        echo -e "${YELLOW}Waiting for Redis...${NC}"
        sleep 2
        REDIS_RUNNING=true
    else
        echo -e "${RED}✗ Redis not available and Docker not found${NC}"
        echo -e "${YELLOW}Please start Redis manually or install Docker${NC}"
        REDIS_RUNNING=false
    fi
fi

# Check ChromaDB
if python -c "import httpx; r = httpx.get('http://localhost:8001/api/v1/heartbeat'); assert r.status_code == 200" &>/dev/null; then
    echo -e "${GREEN}✓ ChromaDB running${NC}"
    CHROMA_RUNNING=true
else
    echo -e "${YELLOW}⚠ ChromaDB not running. RAG features will be limited.${NC}"
    CHROMA_RUNNING=false
fi

echo ""

# --- Initialize database ---
echo -e "${YELLOW}[3/7] Initializing database...${NC}"

if [ "$PG_RUNNING" = true ]; then
    # Run schema
    PGPASSWORD=neobank_secret psql -h localhost -U neobank -d neobank -f ops/init.sql 2>/dev/null || \
    python -c "
import asyncio
import asyncpg

async def init():
    conn = await asyncpg.connect('postgresql://neobank:neobank_secret@localhost:5432/neobank')
    with open('ops/init.sql') as f:
        sql = f.read()
    # Split by semicolons and execute each statement
    for stmt in sql.split(';'):
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--'):
            try:
                await conn.execute(stmt)
            except Exception as e:
                if 'already exists' not in str(e):
                    print(f'Warning: {e}')
    await conn.close()

asyncio.run(init())
" 2>/dev/null || true

    # Load seed data
    python -c "
import asyncio
import asyncpg

async def seed():
    try:
        conn = await asyncpg.connect('postgresql://neobank:neobank_secret@localhost:5432/neobank')
        with open('data/seeds/customers.sql') as f:
            sql = f.read()
        for stmt in sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    await conn.execute(stmt)
                except Exception as e:
                    if 'duplicate' not in str(e) and 'already exists' not in str(e):
                        pass
        await conn.close()
    except Exception as e:
        print(f'Seed warning: {e}')

asyncio.run(seed())
" 2>/dev/null || true

    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${YELLOW}⚠ Skipping database init (PostgreSQL not running)${NC}"
fi

echo ""

# --- Kill existing processes ---
echo -e "${YELLOW}[4/7] Cleaning up existing processes...${NC}"

# Kill existing uvicorn/streamlit processes on our ports
for port in 8000 8501; do
    pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill $pid 2>/dev/null || true
        sleep 1
    fi
done

echo -e "${GREEN}✓ Cleanup done${NC}"
echo ""

# --- Start Agent API ---
echo -e "${YELLOW}[5/7] Starting Agent API (port 8000)...${NC}"

LLM_PROVIDER="${LLM_PROVIDER:-ollama}"
export LLM_PROVIDER

python -m uvicorn services.agent_api.interface.app:create_app \
    --factory \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info &
AGENT_PID=$!

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ Agent API ready${NC}"
        break
    fi
    sleep 1
done

echo ""

# --- Start Ingestion Worker ---
echo -e "${YELLOW}[6/7] Starting Ingestion Worker...${NC}"

python -m services.ingestion_worker.interface.worker &
WORKER_PID=$!

echo -e "${GREEN}✓ Ingestion Worker started${NC}"
echo ""

# --- Start Streamlit ---
echo -e "${YELLOW}[7/7] Starting Streamlit frontend (port 8501)...${NC}"

streamlit run frontend/app.py \
    --server.port 8501 \
    --server.headless false \
    --browser.gatherUsageStats false &
STREAMLIT_PID=$!

# Wait for Streamlit to be ready
echo -e "${YELLOW}Waiting for Streamlit...${NC}"
for i in {1..20}; do
    if curl -s http://localhost:8501 | grep -q "streamlit" 2>/dev/null; then
        echo -e "${GREEN}✓ Streamlit ready${NC}"
        break
    fi
    sleep 1
done

echo ""

# --- Open browser ---
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 All services started! Opening browser...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Agent API:${NC}      http://localhost:8000"
echo -e "  ${GREEN}Streamlit UI:${NC}   http://localhost:8501"
echo -e "  ${GREEN}API Docs:${NC}       http://localhost:8000/docs"
echo -e "  ${GREEN}Health:${NC}         http://localhost:8000/health"
echo ""

# Open browser (works on Linux, macOS, WSL)
if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:8501 2>/dev/null || true
elif command -v open &>/dev/null; then
    open http://localhost:8501 2>/dev/null || true
elif command -v wslview &>/dev/null; then
    wslview http://localhost:8501 2>/dev/null || true
else
    echo -e "${YELLOW}Please open http://localhost:8501 in your browser${NC}"
fi

echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# --- Cleanup on exit ---
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    kill $AGENT_PID 2>/dev/null || true
    kill $WORKER_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    echo -e "${GREEN}✓ All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait -n $AGENT_PID $WORKER_PID $STREAMLIT_PID 2>/dev/null || true
cleanup
