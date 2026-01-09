# Task Manager MVP

A multi-tenant task management web application with user authentication, personal task CRUD operations, and admin user management.

## Features

- **User Authentication**: Register, login, logout with secure password hashing (Argon2)
- **Task Management**: Create, read, update, delete personal tasks
- **Task Status**: Mark tasks complete/incomplete with filtering
- **Admin Panel**: View users, activate/deactivate accounts
- **Data Isolation**: Row-level security ensures users only see their own data

## Tech Stack

- **Backend**: FastAPI (Python 3.12+), SQLAlchemy, Pydantic
- **Database**: PostgreSQL 16 with Row-Level Security
- **Frontend**: SvelteKit 2 (Svelte 5), Tailwind CSS 4
- **Testing**: pytest, Playwright
- **Deployment**: Docker Compose

## Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend E2E tests
cd frontend
npx playwright test
```

## Creating Admin User

```bash
cd backend
python -m app.cli create-admin --email admin@example.com
```

## Project Structure

```
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # Route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── middleware/     # Security headers
│   ├── tests/              # pytest tests
│   └── alembic/            # Database migrations
├── frontend/               # SvelteKit application
│   ├── src/
│   │   ├── lib/            # Components, stores, API
│   │   └── routes/         # Page routes
│   └── tests/              # Playwright tests
├── specs/                  # Feature specifications
└── docker-compose.yml      # Container orchestration
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Authenticate
- `POST /api/auth/logout` - End session
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Current user

### Tasks
- `GET /api/tasks` - List tasks (with filter)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{id}` - Get user details
- `PATCH /api/admin/users/{id}` - Update user status

## License

MIT
