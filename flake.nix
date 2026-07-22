{
  description = "NeoBank Support Chatbot — Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Python with required packages
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          fastapi
          uvicorn
          sse-starlette
          sqlalchemy
          asyncpg
          redis
          litellm
          langchain-core
          langgraph
          pydantic
          pydantic-settings
          httpx
          structlog
          python-dotenv
          pytest
          pytest-asyncio
          pytest-cov
          streamlit
          ruff
          mypy
          sentence-transformers
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.uv
            pkgs.postgresql_16
            pkgs.redis
            pkgs.docker
            pkgs.docker-compose
            pkgs.git
            pkgs.curl
            pkgs.wget
            pkgs.jq
            pkgs.nodejs
            pkgs.prometheus
            pkgs.grafana
          ];

          shellHook = ''
            echo ""
            echo "🏦 NeoBank Support Chatbot — Development Shell (Flake)"
            echo "======================================================"
            echo ""
            echo "Quick start: ./start.sh"
            echo ""

            export PYTHONPATH="$PWD"
            export LLM_PROVIDER="ollama"
            export OLLAMA_BASE_URL="http://localhost:11434"
            export DATABASE_URL="postgresql+asyncpg://neobank:neobank_secret@localhost:5432/neobank"
            export REDIS_URL="redis://localhost:6379/0"
            export CHROMA_HOST="localhost"
            export CHROMA_PORT="8001"

            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc.lib
              pkgs.libgcc
              pkgs.glibc
            ]}:$LD_LIBRARY_PATH"
          '';
        };
      }
    );
}
