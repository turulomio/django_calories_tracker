# Docker & Environment Variables

[![Docker Hub](https://img.shields.io/badge/docker-turulomio%2Fdjango__calories__tracker-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/turulomio/django_calories_tracker)

The official Docker images are available at [Docker Hub: turulomio/django_calories_tracker](https://hub.docker.com/r/turulomio/django_calories_tracker).

Two tags are published:
1. **`turulomio/django_calories_tracker:latest`**: Standard / Production-ready image. Lightweight, requires an external PostgreSQL database configured via environment variables.
2. **`turulomio/django_calories_tracker:e2e`**: Dedicated End-to-End (E2E) testing image. Contains an embedded PostgreSQL server, all Django migrations pre-applied, and test fixtures (`all.json`, `test_server.json`) already pre-loaded into the database during image build. Starts instantly in standalone mode.

---

## 1. Production Image (`turulomio/django_calories_tracker:latest`)

The standard Docker image uses `settings_docker.py`, which inherits from base `settings.py` and allows configuring database connection and server port via environment variables without altering local development configuration.

### Available Variables

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `PORT` | Port where Gunicorn listens | `8000` |
| `POSTGRES_HOST` / `DB_HOST` | Host of the PostgreSQL database | `db` |
| `POSTGRES_PORT` / `DB_PORT` | Port of the PostgreSQL database | `5432` |
| `POSTGRES_DB` / `DB_NAME` | Database name | `calories_tracker` |
| `POSTGRES_USER` / `DB_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` / `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `*` |
| `DEBUG` | Enable/Disable Django debug mode | `True` |
| `CORS_ORIGIN_WHITELIST` | Comma-separated list of allowed CORS origins | `None` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `True` |

### Running with Docker CLI

```bash
# 1. Create network
docker network create calories_net

# 2. Run PostgreSQL container
docker run -d --name calories_db \
  --network calories_net \
  -e POSTGRES_DB=calories_tracker \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  postgres:latest

# 3. Run Django Calories Tracker container
docker run -d --name calories_web \
  --network calories_net \
  -p 8000:8000 \
  -e POSTGRES_HOST=calories_db \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DB=calories_tracker \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  turulomio/django_calories_tracker:latest
```

---

## 2. E2E Testing Image (`turulomio/django_calories_tracker:e2e`)

The E2E image is completely standalone and pre-populated with test fixtures for automated end-to-end testing.

### Running with Docker CLI

```bash
docker run -d --name calories_e2e -p 8011:8000 turulomio/django_calories_tracker:e2e
```

The API will be available immediately at `http://localhost:8011/` with the full test dataset pre-loaded.
