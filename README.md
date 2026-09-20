# 🥗 Django Calories Tracker

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fturulomio%2Fdjango_calories_tracker%2Fbadge%3Fref%3Dmain&style=flat)](https://actions-badge.atrox.dev/turulomio/django_calories_tracker/goto?ref=main)
[![Docker Image](https://img.shields.io/badge/docker-turulomio%2Fdjango__calories__tracker-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/r/turulomio/django_calories_tracker)

This is the backend of the [Calories Tracker](https://github.com/turulomio/calories_tracker) app.

---

## 🐳 Docker Images

Official Docker images are published to Docker Hub at [turulomio/django_calories_tracker](https://hub.docker.com/r/turulomio/django_calories_tracker):

- **`turulomio/django_calories_tracker:latest`**: Production-ready image with Gunicorn, connecting to an external PostgreSQL database via environment variables.
- **`turulomio/django_calories_tracker:e2e`**: Dedicated image for End-to-End (E2E) testing with embedded PostgreSQL and pre-loaded test fixtures (`all.json`, `test_server.json`).

For full details on environment variables, configuration, and execution examples, see [DOCKER.md](DOCKER.md).
