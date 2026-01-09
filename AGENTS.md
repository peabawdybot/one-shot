# AGENTS.md - Task Manager MVP

## Project Overview

Multi-tenant task management application with FastAPI backend, SvelteKit frontend, and PostgreSQL database.

## Commands

### Build & Run

```bash
# Start all services
docker-compose up -d

# Rebuild after changes
docker-compose up -d --build

# Stop services
docker-compose down
```

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Type check (if mypy installed)
mypy app/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Type check
npm run check

# Build for production
npm run build

# Run E2E tests
npm run test:e2e
```

### Database

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U taskmanager -d taskmanager

# Create admin user
cd backend
python -m app.cli create-admin --email admin@example.com
```

## Architecture

- **Backend**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL 16 with Row-Level Security (RLS)
- **Frontend**: SvelteKit 2 with Svelte 5 runes
- **Auth**: JWT access tokens + HTTP-only refresh cookies
- **Styling**: Tailwind CSS 4

## Key Files

- `backend/app/main.py` - FastAPI application entry
- `backend/app/api/` - Route handlers
- `backend/app/models/` - SQLAlchemy models
- `backend/alembic/versions/` - Database migrations
- `frontend/src/routes/` - SvelteKit pages
- `frontend/src/lib/stores/` - Svelte state stores

## Testing

- Backend: pytest with async fixtures
- Frontend: Playwright E2E tests
- Isolation: RLS tests verify data separation

## Environment Variables

See `.env.example` for required configuration.
