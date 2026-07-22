# NeoBank Support Chatbot — Nix development shell
# Run: nix-shell
# Or:  nix-shell --arg devTools true  (with extra dev tools)

{ devTools ? false }:

let
  pkgs = import <nixpkgs> { };

  # Python with required packages
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    # Web framework
    fastapi
    uvicorn
    sse-starlette

    # Data / DB
    sqlalchemy
    asyncpg
    alembic

    # Redis
    redis

    # LLM / AI
    litellm
    langchain-core
    langgraph

    # Utilities
    pydantic
    pydantic-settings
    httpx
    structlog
    python-dotenv

    # Testing
    pytest
    pytest-asyncio
    pytest-cov

    # Frontend
    streamlit

    # Dev tools
    ruff
    mypy
  ]);

in
pkgs.mkShell {
  buildInputs = [
    # === Python ===
    pythonEnv
    pkgs.uv

    # === Databases ===
    pkgs.postgresql_16       # PostgreSQL 16
    pkgs.redis               # Redis

    # === Docker (for containerized services) ===
    pkgs.docker
    pkgs.docker-compose

    # === Dev tools ===
    pkgs.git
    pkgs.curl
    pkgs.wget
    pkgs.jq                  # JSON processing
    pkgs.postgresql          # psql client

    # === Node.js (for Streamlit, optional) ===
    pkgs.nodejs

    # === Monitoring ===
    pkgs.prometheus
    pkgs.grafana
  ] ++ pkgs.lib.optionals devTools [
    # Extra dev tools
    pkgs.ripgrep
    pkgs.fd
    pkgs.bat
    pkgs.lazygit
  ];

  shellHook = ''
    echo ""
    echo "🏦 NeoBank Support Chatbot — Development Shell"
    echo "================================================"
    echo ""
    echo "Available services:"
    echo "  PostgreSQL:  pg_isready || pg_ctl start"
    echo "  Redis:       redis-server --daemonize yes"
    echo "  Docker:      dockerd &"
    echo ""
    echo "Quick start:"
    echo "  ./start.sh    # Start all services and open browser"
    echo ""
    echo "Or manually:"
    echo "  # Start PostgreSQL"
    echo "  initdb -D /tmp/neobank-pg"
    echo "  pg_ctl -D /tmp/neobank-pg start"
    echo "  createdb neobank"
    echo ""
    echo "  # Start Redis"
    echo "  redis-server --daemonize yes"
    echo ""
    echo "  # Start Agent API"
    echo "  PYTHONPATH=. uvicorn services.agent_api.interface.app:create_app --factory --reload"
    echo ""
    echo "  # Start Streamlit"
    echo "  streamlit run frontend/app.py"
    echo ""
    echo "  # Or use the start script"
    echo "  ./start.sh"
    echo ""

    # Set environment variables
    export PYTHONPATH="$PWD"
    export LLM_PROVIDER="ollama"
    export OLLAMA_BASE_URL="http://localhost:11434"
    export DATABASE_URL="postgresql+asyncpg://neobank:neobank_secret@localhost:5432/neobank"
    export REDIS_URL="redis://localhost:6379/0"
    export CHROMA_HOST="localhost"
    export CHROMA_PORT="8001"

    # Set LD_LIBRARY_PATH for NixOS (for litellm, tokenizers, etc.)
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.libgcc
      pkgs.glibc
    ]}:$LD_LIBRARY_PATH"

    echo "Environment configured:"
    echo "  LLM_PROVIDER=$LLM_PROVIDER"
    echo "  DATABASE_URL=$DATABASE_URL"
    echo "  REDIS_URL=$REDIS_URL"
    echo ""
  '';
}
