# IRIS Container Quick Reference

Quick command reference for managing your containerized IRIS dashboard.

## Initial Setup

```bash
# Clone and configure
git clone <repository-url>
cd IRIS-project
cp .env.example .env
nano .env  # Edit your settings
```

## Podman Commands

### Build & Run
```bash
# Build image
podman build -t iris-dashboard .

# Run container (basic)
podman run -d --name iris -p 8080:8080 --env-file .env iris-dashboard

# Run with restart policy
podman run -d --name iris -p 8080:8080 --env-file .env --restart unless-stopped iris-dashboard
```

### Using podman-compose
```bash
# Start (builds if needed)
podman-compose up -d

# Stop
podman-compose down

# View logs
podman-compose logs -f

# Restart
podman-compose restart
```

### Management
```bash
# View running containers
podman ps

# View all containers
podman ps -a

# View logs
podman logs iris
podman logs -f iris      # Follow mode

# Stop/Start/Restart
podman stop iris
podman start iris
podman restart iris

# Remove container
podman rm iris

# Remove image
podman rmi iris-dashboard

# Execute command in container
podman exec iris <command>

# View stats
podman stats iris
```

### Update
```bash
# Pull latest code
git pull

# Rebuild and restart
podman stop iris
podman rm iris
podman build -t iris-dashboard .
podman run -d --name iris -p 8080:8080 --env-file .env --restart unless-stopped iris-dashboard
```

## Docker Commands

Replace `podman` with `docker` in all commands above:

```bash
# Build & Run
docker build -t iris-dashboard .
docker run -d --name iris -p 8080:8080 --env-file .env --restart unless-stopped iris-dashboard

# Using docker-compose
docker-compose up -d
docker-compose down
docker-compose logs -f

# Management
docker ps
docker logs iris
docker stop iris
docker start iris
docker restart iris
docker rm iris
docker rmi iris-dashboard
```

## Common Tasks

### Check if IRIS is Running
```bash
podman ps | grep iris
curl http://localhost:8080/health
```

### View Recent Logs
```bash
podman logs --tail 50 iris
```

### Update Configuration
```bash
# Edit .env file
nano .env

# Restart container to apply changes
podman restart iris
```

### Troubleshoot Connection Issues
```bash
# Check if container is running
podman ps

# Check logs for errors
podman logs iris

# Verify port is open
sudo ss -tulpn | grep :8080

# Test health endpoint
curl http://localhost:8080/health
```

### Run on Different Port
```bash
# Edit .env
echo "SERVER_PORT=3000" >> .env

# Run with new port
podman run -d --name iris -p 3000:8080 --env-file .env iris-dashboard
```

### Clean Everything
```bash
# Stop and remove container
podman stop iris && podman rm iris

# Remove image
podman rmi iris-dashboard

# Remove all unused images (careful!)
podman image prune -a
```

## Access Points

- Dashboard: http://localhost:8080
- Tech News: http://localhost:8080/tech-news
- Health Check: http://localhost:8080/health
- Config: http://localhost:8080/config

## Environment Variables

Edit `.env` file to configure:

```bash
USER_NAME=YourName
PRIMARY_CITY=YourCity
PRIMARY_LATITUDE=12.3456
PRIMARY_LONGITUDE=-12.3456
SECONDARY_CITY=SecondCity
SECONDARY_LATITUDE=23.4567
SECONDARY_LONGITUDE=-23.4567
SERVER_PORT=8080
UPDATE_INTERVAL=300
DEBUG_MODE=false
```

## Systemd Auto-Start (Podman)

```bash
# Generate service file
cd ~/.config/systemd/user
podman generate systemd --new --files --name iris

# Enable and start
systemctl --user enable container-iris.service
systemctl --user start container-iris.service

# Check status
systemctl --user status container-iris.service
```

## Resource Limits

```bash
# Limit memory and CPU
podman run -d \
  --name iris \
  -p 8080:8080 \
  --env-file .env \
  --memory=512m \
  --cpus=1 \
  iris-dashboard
```

## Need Help?

- Full guide: [docs/container_setup.md](container_setup.md)
- Summary: [docs/CONTAINERIZATION_SUMMARY.md](CONTAINERIZATION_SUMMARY.md)
- Main README: [README.md](../README.md)
