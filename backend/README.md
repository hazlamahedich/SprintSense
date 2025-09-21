# SprintSense Backend

FastAPI backend for the SprintSense AI-powered agile project management platform.

## Development

```bash
# Install dependencies
poetry install

# Run the server
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest

# Run linting
poetry run black .
poetry run isort .
poetry run flake8 .
```

## Configuration

Set environment variables or create a `.env` file:

- `POSTGRES_SERVER` - PostgreSQL server hostname
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - PostgreSQL database name
- `ENVIRONMENT` - Environment (development/production)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)

