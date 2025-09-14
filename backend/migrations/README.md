# TECHGURU ElevateCRM Database Migrations

This directory contains Alembic database migrations for the ElevateCRM platform.

## Usage

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Downgrade migrations  
alembic downgrade -1
```
