"""
Docker-specific Django settings for django_calories_tracker.

This module inherits all settings from the base `settings.py` module and allows
customizing configurations such as database connections, allowed hosts, CORS,
and server ports dynamically through environment variables.
"""

import os
from .settings import *

# ==============================================================================
# Database Configuration
# ==============================================================================
# Overrides default PostgreSQL connection parameters using environment variables.
DATABASES['default']['HOST'] = os.environ.get('POSTGRES_HOST', os.environ.get('DB_HOST', 'db'))
DATABASES['default']['PORT'] = int(os.environ.get('POSTGRES_PORT', os.environ.get('DB_PORT', '5432')))
DATABASES['default']['NAME'] = os.environ.get('POSTGRES_DB', os.environ.get('DB_NAME', 'calories_tracker'))
DATABASES['default']['USER'] = os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', 'postgres'))
DATABASES['default']['PASSWORD'] = os.environ.get('POSTGRES_PASSWORD', os.environ.get('DB_PASSWORD', 'postgres'))

# ==============================================================================
# Security & Hosts
# ==============================================================================
# Configures ALLOWED_HOSTS from a comma-separated environment variable or defaults to wildcard for container setups.
_env_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '*')
if _env_allowed_hosts:
    ALLOWED_HOSTS = [host.strip() for host in _env_allowed_hosts.split(',') if host.strip()]

# Allows controlling DEBUG mode via environment variable (default: True for local/dev containers)
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't', 'yes')

# ==============================================================================
# CORS Configuration
# ==============================================================================
# Optional CORS whitelist override from comma-separated origins.
_env_cors_whitelist = os.environ.get('CORS_ORIGIN_WHITELIST')
if _env_cors_whitelist:
    CORS_ORIGIN_WHITELIST = tuple(origin.strip() for origin in _env_cors_whitelist.split(',') if origin.strip())
else:
    # Allow all origins by default in Docker development/e2e environment unless specified
    CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1', 't', 'yes')
