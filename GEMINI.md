# Project Guidelines & Rules for Django Calories Tracker

## General Instructions
- **Code Documentation**: Always document all code written or modified.
  - Add descriptive docstrings to modules, classes, methods, and functions specifying purpose, parameters, return types, and exceptions where appropriate.
  - Include inline comments explaining non-trivial logic, edge cases, and architectural decisions.
  - Preserve and update existing documentation when modifying code.

## Technology Stack & Architecture
- **Language & Runtime**: Python >= 3.12.
- **Framework**: Django >= 6.0, Django REST Framework (DRF), django-simple-history.
- **Package & Task Management**: Poetry (`poetry run ...`), PoeThePoet (`poe ...`).
- **Database**: PostgreSQL (psycopg3).

## Coding Standards & Conventions
- **Code Style**: Follow PEP 8 standards with clean, readable, and idiomatic Python.
- **Django/DRF Conventions**:
  - Keep business logic in appropriate layers (models/services/serializers) and keep views clean.
  - Maintain serializers and API schema definitions (DRF Spectacular) synchronized with models.
  - Follow existing conventions in `calories_tracker/` for models, serializers, views, permissions, and management commands.

## Testing & Quality Assurance
- Ensure changes pass test suites and do not break existing test coverage.
- Write unit/integration tests for new features and bugfixes under `calories_tracker/tests/`.
