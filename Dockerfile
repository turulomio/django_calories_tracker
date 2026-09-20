# --- Stage 1: Build dependencies ---
FROM python:3.14-slim-bookworm AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and export plugin
RUN pip install poetry && poetry self add poetry-plugin-export

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Export dependencies to requirements.txt and build wheels
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip wheel --no-cache-dir --wheel-dir=/usr/src/app/wheels -r requirements.txt

# --- Stage 2: Final production image ---
FROM python:3.14-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install runtime dependencies (libpq for psycopg, exiftool & libmagic for preview-generator)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libpq-dev \
    exiftool \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Install dependencies from wheels and gunicorn
RUN pip install --no-cache-dir /wheels/* -r requirements.txt gunicorn

# Create a non-root system user and prepare directories
RUN adduser --system --group appuser \
    && mkdir -p /tmp/django_calories_tracker-appuser \
    && chown -R appuser:appuser /tmp/django_calories_tracker-appuser

# Copy application source code into the container
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Expose server port
EXPOSE 8000

# Django environment variables
ENV DJANGO_SETTINGS_MODULE=django_calories_tracker.settings_docker
ENV PORT=8000
ENV POSTGRES_DB=calories_tracker
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

# Run Gunicorn WSGI server
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} django_calories_tracker.wsgi:application"]
