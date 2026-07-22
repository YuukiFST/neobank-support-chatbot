#!/usr/bin/env bash
# NeoBank Support Chatbot — NixOS Setup Helper
# Helps configure NixOS with required services

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🏦 NeoBank — NixOS Setup Helper${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}✗ Do not run as root!${NC}"
    echo -e "${YELLOW}Run without sudo, the script will ask for sudo when needed.${NC}"
    exit 1
fi

# Check if on NixOS
if [ ! -f /etc/nixos/configuration.nix ]; then
    echo -e "${RED}✗ This script is for NixOS only.${NC}"
    exit 1
fi

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Backup your current NixOS configuration"
echo "  2. Add required services (PostgreSQL, Redis, Docker)"
echo "  3. Rebuild NixOS configuration"
echo ""
echo -e "${YELLOW}Services to be enabled:${NC}"
echo "  • PostgreSQL 16 (port 5432)"
echo "  • Redis (port 6379)"
echo "  • Docker"
echo "  • User 'yuuki' added to docker group"
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Backup current configuration
echo ""
echo -e "${YELLOW}[1/4] Backing up current configuration...${NC}"

BACKUP_DIR="/etc/nixos/backup-$(date +%Y%m%d-%H%M%S)"
sudo mkdir -p "$BACKUP_DIR"
sudo cp /etc/nixos/configuration.nix "$BACKUP_DIR/"
sudo cp /etc/nixos/hardware-configuration.nix "$BACKUP_DIR/"

echo -e "${GREEN}✓ Backup created at $BACKUP_DIR${NC}"

# Check if services are already configured
echo ""
echo -e "${YELLOW}[2/4] Checking current configuration...${NC}"

CONFIG="/etc/nixos/configuration.nix"

if grep -q "services.postgresql" "$CONFIG"; then
    echo -e "${YELLOW}⚠ PostgreSQL already configured${NC}"
else
    echo -e "${YELLOW}Adding PostgreSQL configuration...${NC}"
    # Add PostgreSQL config before the last closing brace
    sudo sed -i '/^}$/i\
  # === PostgreSQL ===\
  services.postgresql = {\
    enable = true;\
    package = pkgs.postgresql_16;\
    port = 5432;\
    settings = {\
      max_connections = 100;\
      shared_buffers = "256MB";\
      effective_cache_size = "1GB";\
    };\
    initialScript = '\''\
      CREATE USER neobank WITH PASSWORD '\''neobank_secret'\'';\
      CREATE DATABASE neobank OWNER neobank;\
      GRANT ALL PRIVILEGES ON DATABASE neobank TO neobank;\
    '\'';\
  };\
' "$CONFIG"
    echo -e "${GREEN}✓ PostgreSQL added${NC}"
fi

if grep -q "services.redis" "$CONFIG"; then
    echo -e "${YELLOW}⚠ Redis already configured${NC}"
else
    echo -e "${YELLOW}Adding Redis configuration...${NC}"
    sudo sed -i '/^}$/i\
  # === Redis ===\
  services.redis.servers."neobank" = {\
    enable = true;\
    port = 6379;\
    bind = "127.0.0.1";\
    settings = {\
      maxmemory = "256mb";\
      maxmemory-policy = "allkeys-lru";\
    };\
  };\
' "$CONFIG"
    echo -e "${GREEN}✓ Redis added${NC}"
fi

if grep -q "virtualisation.docker" "$CONFIG"; then
    echo -e "${YELLOW}⚠ Docker already configured${NC}"
else
    echo -e "${YELLOW}Adding Docker configuration...${NC}"
    sudo sed -i '/^}$/i\
  # === Docker ===\
  virtualisation.docker = {\
    enable = true;\
    autoPrune.enable = true;\
  };\
  users.users.yuuki.extraGroups = [ "docker" ];\
' "$CONFIG"
    echo -e "${GREEN}✓ Docker added${NC}"
fi

# Add firewall rules
if ! grep -q "networking.firewall.allowedTCPPorts" "$CONFIG"; then
    echo -e "${YELLOW}Adding firewall rules...${NC}"
    sudo sed -i '/^}$/i\
  # === Firewall ===\
  networking.firewall.allowedTCPPorts = [ 5432 6379 8000 8001 8501 ];\
' "$CONFIG"
    echo -e "${GREEN}✓ Firewall rules added${NC}"
fi

# Rebuild NixOS
echo ""
echo -e "${YELLOW}[3/4] Rebuilding NixOS configuration...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}"

sudo nixos-rebuild switch 2>&1 | tail -20

echo ""

# Verify services
echo -e "${YELLOW}[4/4] Verifying services...${NC}"

# Check PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not running yet (may need reboot)${NC}"
fi

# Check Redis
if systemctl is-active --quiet redis-neobank; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠ Redis not running yet (may need reboot)${NC}"
fi

# Check Docker
if systemctl is-active --quiet docker; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${YELLOW}⚠ Docker not running yet (may need reboot)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ NixOS setup complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. If services are not running, reboot your system"
echo "  2. Run: ./start.sh"
echo "  3. Open browser to http://localhost:8501"
echo ""
echo -e "${YELLOW}Or use nix-shell for a development environment:${NC}"
echo "  nix-shell"
echo ""
