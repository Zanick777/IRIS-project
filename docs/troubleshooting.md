# Troubleshooting

This document aggregates troubleshooting steps from the project documentation and startup scripts. Sections are grouped by workflow: Local start up (native Python) and Container start up (Docker/Podman), plus general diagnostics.

---

## Local start up

When running IRIS natively (not in a container). See [START_HERE.txt](START_HERE.txt) and [QUICKSTART.md](QUICKSTART.md) for original context.

- Symptom: `ModuleNotFoundError` (missing Python packages)
  - Fix: Install required packages:
    ```bash
    pip3 install --user aiohttp python-socketio python-dotenv
    ```

- Symptom: Server not starting / "Connecting..." in UI
  - Check server health endpoint:
    ```bash
    curl http://localhost:8080/health
    ```
    - Expected response: `{"status": "online", "active_clients": 0, "timestamp": "..."}`
  - Ensure server process is running:
    ```bash
    ps aux | grep dashboard_server.py
    ```

- Symptom: Port 8080 already in use
  - Fix: Kill existing server/process using the port:
    ```bash
    pkill -f dashboard_server.py
    ```
  - Or find and kill specific PID:
    ```bash
    sudo ss -tulpn | grep :8080
    sudo kill <PID>
    ```

- Symptom: No data / empty news or missing API data
  - Wait 1–2 minutes for initial data fetch and refresh the UI
  - Check server logs for errors (if running in background):
    ```bash
    tail -f iris.log
    ```
  - Look for API-specific errors (e.g., HTTP 404, missing JSON keys)

- Running in background
  - Start in background (nohup):
    ```bash
    nohup python3 dashboard_server.py > iris.log 2>&1 &
    ```
  - Stop background server:
    ```bash
    pkill -f dashboard_server.py
    ```

- Environment variables (.env)
  - Ensure `.env` exists and contains required variables (copy from `.env.example`):
    ```bash
    cp .env.example .env
    nano .env
    ```
  - Required variables: `USER_NAME`, `PRIMARY_CITY`, `PRIMARY_LATITUDE`, `PRIMARY_LONGITUDE`, etc.
  - If you change `.env`, restart the server to pick up changes.

- Systemd service troubleshooting
  - If using a systemd service, check status and logs:
    ```bash
    sudo systemctl status iris
    sudo journalctl -u iris -f
    ```

---

## Container start up

When running IRIS inside Docker or Podman containers. See [docs/container_setup.md](container_setup.md) and [docs/CONTAINER_QUICKREF.md](CONTAINER_QUICKREF.md).

- Verify container is running
  - Podman:
    ```bash
    podman ps | grep iris
    ```
  - Docker:
    ```bash
    docker ps | grep iris
    ```

- Check container logs for errors
  - Podman:
    ```bash
    podman logs iris
    podman logs -f iris  # follow
    ```
  - Docker:
    ```bash
    docker logs iris
    docker logs -f iris
    ```

- Health endpoint inside container
  - Test host mapping of health endpoint:
    ```bash
    curl http://localhost:8080/health
    ```
  - If not reachable, verify port mapping (container port -> host port) and firewall rules.

- Port conflict
  - If host port `8080` is in use, run container with different host port:
    ```bash
    podman run -d --name iris -p 3000:8080 --env-file .env iris-dashboard
    ```

- Rebuild/update container
  - Pull latest code, rebuild image, and recreate container:
    ```bash
    git pull
    podman-compose down
    podman-compose build
    podman-compose up -d
    ```
  - Or with Docker:
    ```bash
    docker-compose down
    docker-compose build
    docker-compose up -d
    ```

- Podman/docker-compose troubleshooting commands
  - View logs: `podman-compose logs -f` or `docker-compose logs -f`
  - Restart: `podman-compose restart` or `docker-compose restart`
  - Check containers: `podman ps -a` / `docker ps -a`

- Permissions / Podman rootless issues
  - Ensure podman/docker have correct permissions and user mappings. If bind ports <1024 are used, elevated permissions may be required.

---

## Health checks & logs

- Health endpoint: `http://localhost:8080/health` — primary quick check for server health.
- Application logs:
  - Local start: `iris.log` (if started with `nohup`) or console output.
  - Containers: `podman logs iris` / `docker logs iris`.
- Common log errors to watch for:
  - `ModuleNotFoundError` -> install missing packages
  - `HTTP 4xx/5xx` from external APIs -> external data provider issue
  - JSON/key errors (e.g., `Error fetching XRP data: 'prices'`) -> API response changed or missing fields

---

## Network & ports

- Confirm server is listening on expected port:
  ```bash
  sudo ss -tulpn | grep :8080
  ```
- To access from other devices, ensure host binds to `0.0.0.0` and firewall allows incoming connections on the mapped port. Use `hostname -I` to find host IP.

---

## Data feeds & API errors

- If a specific feed fails (e.g., news category or XRP prices):
  - Check logs for lines like `Failed to fetch US Politics: HTTP 404` or `Error fetching XRP data: 'prices'`.
  - These indicate either a remote feed changed/removed or the parsing code expects a different JSON shape.
  - Temporary solutions: retry later; longer-term: update parser or switch feed.

---

## Quick commands summary

- Start local server (recommended):
  ```bash
  ./start_iris.sh
  ```
- Start local server manually:
  ```bash
  python3 dashboard_server.py
  ```
- Install dependencies:
  ```bash
  pip3 install --user aiohttp python-socketio python-dotenv
  ```
- Check health:
  ```bash
  curl http://localhost:8080/health
  ```
- View logs (background):
  ```bash
  tail -f iris.log
  ```
- Stop server:
  ```bash
  pkill -f dashboard_server.py
  ```
- Container logs:
  ```bash
  podman logs iris
  docker logs iris
  ```

---

## Where this information came from

- [START_HERE.txt](START_HERE.txt)
- [QUICKSTART.md](QUICKSTART.md)
- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [docs/container_setup.md](container_setup.md)
- [docs/CONTAINER_QUICKREF.md](CONTAINER_QUICKREF.md)
- [docs/CONTAINERIZATION_SUMMARY.md](CONTAINERIZATION_SUMMARY.md)

If you want, I can also add this troubleshooting doc to the README or link it from other docs.
