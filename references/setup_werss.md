# WeRSS and Docker Setup

Use this reference when the user needs to install, upgrade, or diagnose WeRSS/Docker.

## Public Sources

- Docker Desktop official install docs:
  - Windows: https://docs.docker.com/desktop/setup/install/windows-install/
  - Mac: https://docs.docker.com/installation/mac/
  - Linux: https://docs.docker.com/desktop/setup/install/linux/
- Docker Engine official install docs for Linux servers: https://docs.docker.com/engine/install/
- WeRSS / we-mp-rss upstream repository: https://github.com/rachelos/we-mp-rss

## Docker Boundary

Do not install Docker silently. Ask the user before downloading installers or changing system services. Docker Desktop licensing terms may matter for commercial or enterprise use; ask the user to confirm their environment before recommending Desktop as the final production choice.

For most local personal/workstation use, Docker Desktop is the easiest route. For Linux servers, Docker Engine is often more appropriate.

## WeRSS Quick Start

The upstream project currently documents this Docker image pattern:

```bash
docker run -d --name we-mp-rss -p 8001:8001 -v ./data:/app/data ghcr.io/rachelos/we-mp-rss:latest
```

This skill also provides a compose-file generator:

```powershell
python scripts\industryctl.py write-werss-compose --project .\my-digest-project
```

Then start it from the project folder:

```powershell
docker compose -f docker-compose.werss.yml up -d
```

Open:

```text
http://localhost:8001/
```

If WeRSS requests login, QR authorization, or other user interaction, pause and let the user complete it. Do not ask the assistant to extract cookies or bypass access controls.

## Upgrade Pattern

Use an explicit user-approved upgrade flow:

```bash
docker compose -f docker-compose.werss.yml pull
docker compose -f docker-compose.werss.yml up -d
```

Before upgrade, make sure the WeRSS data directory is backed up. The default generated compose file stores data in:

```text
./werss-data
```

## DB Discovery

The generated config defaults to:

```json
"db_glob": "./werss-data/**/*"
```

If the user already has WeRSS elsewhere, update `config/config.json` with either:

- `werss.db_path`: exact path to `db.db`; or
- `werss.db_glob`: glob pattern that finds a WeRSS SQLite DB.

The helper recognizes common WeRSS SQLite filenames:

- `db.db`
- `database.sqlite`
