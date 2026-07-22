# NeoBank Support Chatbot — NixOS system configuration snippet
# Add this to /etc/nixos/configuration.nix to enable required services
#
# Usage:
#   1. Copy relevant sections to your configuration.nix
#   2. Run: sudo nixos-rebuild switch
#   3. Then run: ./start.sh

{ config, pkgs, ... }:

{
  # === Enable Docker ===
  virtualisation.docker = {
    enable = true;
    autoPrune.enable = true;
    storageDriver = "btrfs";
  };

  # Add user to docker group
  users.users.yuuki.extraGroups = [ "docker" ];

  # === Enable PostgreSQL ===
  services.postgresql = {
    enable = true;
    package = pkgs.postgresql_16;
    port = 5432;
    settings = {
      max_connections = 100;
      shared_buffers = "256MB";
      effective_cache_size = "1GB";
    };
    initialScript = ''
      CREATE USER neobank WITH PASSWORD 'neobank_secret';
      CREATE DATABASE neobank OWNER neobank;
      GRANT ALL PRIVILEGES ON DATABASE neobank TO neobank;
    '';
  };

  # === Enable Redis ===
  services.redis = {
    servers."neobank" = {
      enable = true;
      port = 6379;
      bind = "127.0.0.1";
      settings = {
        maxmemory = "256mb";
        maxmemory-policy = "allkeys-lru";
      };
    };
  };

  # === Optional: Enable Prometheus ===
  services.prometheus = {
    enable = false;  # Set to true if you want system-wide Prometheus
    port = 9090;
    exporters = {
      node = {
        enable = true;
        port = 9100;
      };
    };
  };

  # === Optional: Enable Grafana ===
  services.grafana = {
    enable = false;  # Set to true if you want system-wide Grafana
    settings = {
      server.http_port = 3001;
    };
  };

  # === Additional system packages ===
  environment.systemPackages = with pkgs; [
    # Databases
    postgresql_16
    redis

    # Docker tools
    docker-compose
    lazydocker

    # Monitoring
    prometheus
    grafana

    # Development
    python3
    uv
  ];

  # === Open firewall ports (if needed) ===
  networking.firewall = {
    allowedTCPPorts = [
      5432   # PostgreSQL
      6379   # Redis
      8000   # Agent API
      8001   # ChromaDB
      8501   # Streamlit
      9090   # Prometheus
      3001   # Grafana
    ];
  };
}
