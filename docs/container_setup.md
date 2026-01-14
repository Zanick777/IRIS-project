# IRIS Container Deployment Guide

This guide covers how to deploy IRIS - Intelligent Reasoning and Interface System using Docker or Podman containers. Container deployment is the recommended method as it ensures consistent behavior across all environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start with Podman](#quick-start-with-podman)
- [Quick Start with Docker](#quick-start-with-docker)
- [Configuration](#configuration)
- [Container Management](#container-management)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### For Podman (Recommended)
- Podman installed ([Installation Guide](https://podman.io/getting-started/installation))
- podman-compose (optional, for docker-compose compatibility)
  ```bash
  pip3 install --user podman-compose
  ```

### For Docker
- Docker installed ([Installation Guide](https://docs.docker.com/get-docker/))
- docker-compose (usually included with Docker Desktop)

### Common Requirements
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection for fetching data from APIs

## Quick Start with Podman

### Method 1: Using podman-compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/iris-dashboard.git
   cd iris-dashboard
   ```

2. **Configure your environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your preferences
   ```

3. **Start the container**
   ```bash
   podman-compose up -d
   ```

4. **Access the dashboard**
   - Open your browser to: http://localhost:8080
   - The dashboard will automatically connect and start streaming data

### Method 2: Using Podman directly

1. **Build the image**
   ```bash
   podman build -t iris-dashboard .
   ```

2. **Run the container**
   ```bash
   podman run -d \
     --name iris \
     -p 8080:8080 \
     --env-file .env \
     --restart unless-stopped \
     iris-dashboard
   ```

3. **Verify it's running**
   ```bash
   podman ps
   podman logs iris
   ```

## Quick Start with Docker

### Method 1: Using docker-compose (Recommended)

1. **Clone and configure**
   ```bash
   git clone https://github.com/yourusername/iris-dashboard.git
   cd iris-dashboard
   cp .env.example .env
   nano .env  # Edit with your preferences
   ```

2. **Start the container**
   ```bash
   docker-compose up -d
   ```

3. **Access the dashboard**
   - Navigate to: http://localhost:8080

### Method 2: Using Docker directly

1. **Build the image**
   ```bash
   docker build -t iris-dashboard .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name iris \
     -p 8080:8080 \
     --env-file .env \
     --restart unless-stopped \
     iris-dashboard
   ```

3. **Verify it's running**
   ```bash
   docker ps
   docker logs iris
   ```

## Configuration

### Environment Variables

IRIS uses environment variables for all configuration. Create a `.env` file from the example:

```bash
cp .env.example .env
```

#### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `USER_NAME` | Your name for personalized greetings | `Zack` |
| `PRIMARY_CITY` | Your primary location name | `Irving` |
| `PRIMARY_LATITUDE` | Latitude of primary location | `32.8140` |
| `PRIMARY_LONGITUDE` | Longitude of primary location | `-96.9489` |
| `SECONDARY_CITY` | Your secondary location name | `Lewisville` |
| `SECONDARY_LATITUDE` | Latitude of secondary location | `33.0462` |
| `SECONDARY_LONGITUDE` | Longitude of secondary location | `-96.9942` |

#### Optional Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVER_HOST` | Server bind address | `0.0.0.0` |
| `SERVER_PORT` | Server port number | `8080` |
| `UPDATE_INTERVAL` | Data refresh interval (seconds) | `300` |
| `DEBUG_MODE` | Enable debug logging | `false` |

### Finding Your Coordinates

**Option 1: LatLong.net**
- Visit [LatLong.net](https://www.latlong.net/)
- Search for your city
- Copy the latitude and longitude values

**Option 2: Google Maps**
- Right-click on your location in Google Maps
- Click the coordinates at the top to copy them
- Format: latitude, longitude

## Container Management

### Podman Commands

#### View running containers
```bash
podman ps
```

#### View all containers (including stopped)
```bash
podman ps -a
```

#### View container logs
```bash
podman logs iris
podman logs -f iris  # Follow logs in real-time
```

#### Stop the container
```bash
podman stop iris
# Or with podman-compose
podman-compose down
```

#### Start the container
```bash
podman start iris
# Or with podman-compose
podman-compose up -d
```

#### Restart the container
```bash
podman restart iris
# Or with podman-compose
podman-compose restart
```

#### Remove the container
```bash
podman stop iris
podman rm iris
```

#### Remove the image
```bash
podman rmi iris-dashboard
```

#### Update to latest version
```bash
git pull
podman-compose down
podman-compose build
podman-compose up -d
```

### Docker Commands

The Docker commands are identical to Podman, just replace `podman` with `docker`:

```bash
# View logs
docker logs iris

# Stop container
docker stop iris

# Start container
docker start iris

# Restart container
docker restart iris

# Update to latest
docker-compose down
docker-compose build
docker-compose up -d
```

## Advanced Usage

### Custom Port Mapping

To run IRIS on a different port (e.g., 3000):

**Using compose:**
Edit `.env` file:
```bash
SERVER_PORT=3000
```

Then restart:
```bash
podman-compose down && podman-compose up -d
```

**Using Podman/Docker directly:**
```bash
podman run -d \
  --name iris \
  -p 3000:8080 \
  --env-file .env \
  iris-dashboard
```

### Running Multiple Instances

You can run multiple IRIS instances with different configurations:

```bash
# Instance 1: Personal Dashboard (port 8080)
podman run -d \
  --name iris-personal \
  -p 8080:8080 \
  --env-file .env.personal \
  iris-dashboard

# Instance 2: Office Dashboard (port 8081)
podman run -d \
  --name iris-office \
  -p 8081:8080 \
  --env-file .env.office \
  iris-dashboard
```

### Accessing from Other Devices

The container binds to `0.0.0.0` by default, allowing access from other devices:

1. Find your machine's IP address:
   ```bash
   hostname -I  # Linux
   ipconfig     # Windows
   ifconfig     # macOS
   ```

2. Access from another device:
   ```
   http://YOUR_IP_ADDRESS:8080
   ```

### Running as a Systemd Service (Podman)

For automatic startup on boot with Podman:

1. **Generate systemd unit file:**
   ```bash
   cd ~/.config/systemd/user
   podman generate systemd --new --files --name iris
   ```

2. **Enable and start the service:**
   ```bash
   systemctl --user enable container-iris.service
   systemctl --user start container-iris.service
   ```

3. **Check status:**
   ```bash
   systemctl --user status container-iris.service
   ```

### Resource Limits

To limit container resource usage:

**Podman:**
```bash
podman run -d \
  --name iris \
  -p 8080:8080 \
  --env-file .env \
  --memory=512m \
  --cpus=1 \
  iris-dashboard
```

**Docker Compose:**
Add to `docker-compose.yml`:
```yaml
services:
  iris:
    # ... other settings ...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Health Checks

The container includes a built-in health check. View health status:

```bash
# Podman
podman inspect iris | grep -A 10 Health

# Docker
docker inspect iris | grep -A 10 Health
```

## Troubleshooting

### Container won't start

**Check logs:**
```bash
podman logs iris
```

**Common issues:**
- Port 8080 already in use: Change the port mapping
- Invalid .env file: Verify environment variable syntax
- Permission issues: Ensure Podman/Docker has proper permissions

### Dashboard shows "Connecting..." but never connects

1. **Verify container is running:**
   ```bash
   podman ps
   ```

2. **Check health endpoint:**
   ```bash
   curl http://localhost:8080/health
   ```

3. **Inspect logs for errors:**
   ```bash
   podman logs iris
   ```

4. **Restart the container:**
   ```bash
   podman restart iris
   ```

### Data not updating

1. **Check internet connectivity from container:**
   ```bash
   podman exec iris curl https://api.coingecko.com/api/v3/ping
   ```

2. **Verify update interval in .env:**
   ```bash
   grep UPDATE_INTERVAL .env
   ```

3. **Check container logs for API errors:**
   ```bash
   podman logs iris | grep -i error
   ```

### Port already in use

**Find what's using the port:**
```bash
sudo ss -tulpn | grep :8080
```

**Change IRIS to use a different port:**
Edit `.env`:
```bash
SERVER_PORT=8081
```

Then rebuild:
```bash
podman-compose down && podman-compose up -d
```

### Container uses too much memory/CPU

**Check resource usage:**
```bash
podman stats iris
```

**Apply resource limits:**
```bash
podman update --memory=512m --cpus=1 iris
```

### Podman-compose not found

**Install podman-compose:**
```bash
pip3 install --user podman-compose
```

**Or use Podman directly:**
```bash
podman play kube docker-compose.yml
```

### Permission denied errors

**For Podman (rootless):**
```bash
# Ensure subuid/subgid are configured
grep $USER /etc/subuid /etc/subgid

# Reset Podman if needed
podman system reset
```

**For Docker:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Best Practices

1. **Always use .env files** - Never hardcode sensitive information
2. **Keep .env out of version control** - Already in .gitignore
3. **Use podman-compose/docker-compose** - Easier management than direct commands
4. **Monitor logs regularly** - Catch issues early
5. **Update regularly** - Pull latest changes and rebuild
6. **Use health checks** - Ensure container is functioning properly
7. **Set resource limits** - Prevent resource exhaustion
8. **Backup your .env** - Store configuration securely

## Next Steps

- Customize your dashboard appearance
- Add systemd service for auto-start
- Set up reverse proxy (nginx/traefik) for HTTPS
- Configure firewall rules for remote access
- Explore the tech news page at `/tech-news`

## Support

For issues, questions, or contributions:
- Check the main [README.md](../README.md)
- Review [QUICKSTART.md](../QUICKSTART.md)
- Check container logs for errors
- Ensure all prerequisites are met
