# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Versatex Analytics - An enterprise-grade procurement analytics platform with organization-based multi-tenancy.

**Tech Stack:**
- Backend: Django 5.0 + Django REST Framework + PostgreSQL + Celery/Redis
- Frontend: React 18 + TypeScript + Tailwind CSS 4 + Vite
- Auth: JWT tokens with role-based access (admin, manager, viewer)

## Development Commands

### Docker Development (Recommended)

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files (after changing backend/static/)
docker-compose exec backend python manage.py collectstatic --noinput

# Force rebuild frontend (when changes aren't reflected)
docker-compose up -d --build --force-recreate frontend
```

### Local Development

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py runserver

# Frontend
cd frontend
pnpm install
pnpm dev
```

### Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test
docker-compose exec backend python manage.py test apps.authentication  # specific app

# Frontend tests
cd frontend
pnpm test           # watch mode
pnpm test:run       # single run
pnpm test:ui        # with UI
```

### Type Checking & Formatting

```bash
cd frontend
pnpm check          # TypeScript check (tsc --noEmit)
pnpm format         # Prettier
```

## Architecture

### Backend Structure (`backend/`)

```
backend/
├── apps/
│   ├── authentication/     # User, Organization, UserProfile, AuditLog models
│   ├── procurement/        # Supplier, Category, Transaction, DataUpload models
│   └── analytics/          # AnalyticsService - all analytics calculations
├── config/                 # Django settings, URLs, Celery config
└── templates/admin/        # Custom Django admin templates (navy theme)
```

**Key Patterns:**
- All data models are scoped by `organization` ForeignKey for multi-tenancy
- `AnalyticsService` class in `apps/analytics/services.py` handles all analytics calculations
- JWT auth via djangorestframework-simplejwt with token refresh
- CSRF exempt on LoginView for frontend API calls

### Frontend Structure (`frontend/src/`)

```
src/
├── components/
│   ├── ui/                 # shadcn/ui components (Radix primitives)
│   ├── DashboardLayout.tsx # Main layout with sidebar navigation
│   └── ProtectedRoute.tsx  # Auth guard component
├── contexts/
│   ├── AuthContext.tsx     # Auth state (isAuth, checkAuth, logout)
│   └── ThemeContext.tsx    # Light/dark theme
├── hooks/
│   ├── useAnalytics.ts     # Analytics data fetching
│   ├── useFilters.ts       # Filter state management
│   └── useProcurementData.ts # Transaction data fetching
├── lib/
│   ├── api.ts              # Axios client with auth interceptors
│   ├── auth.ts             # Auth API functions
│   └── analytics.ts        # Analytics calculations (client-side)
└── pages/                  # Route components (lazy-loaded)
```

**Key Patterns:**
- Wouter for routing (not React Router)
- TanStack Query for data fetching
- All pages lazy-loaded for code splitting
- Auth state in localStorage (`access_token`, `refresh_token`, `user`)
- Admin panel link only shown when `user.profile.role === 'admin'`

### API Structure

```
/api/v1/auth/          # login, register, logout, token/refresh, user
/api/v1/procurement/   # suppliers, categories, transactions (CRUD + upload_csv, bulk_delete, export)
/api/v1/analytics/     # overview, spend-by-category, pareto, tail-spend, etc.
```

Legacy endpoints (`/api/auth/`, `/api/procurement/`, `/api/analytics/`) are supported for backwards compatibility.

## Port Configuration

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8001/api` (maps to container port 8000)
- Django Admin: `http://localhost:8001/admin`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Environment Variables

### Root `.env` (for Docker)

```env
DB_NAME=analytics_db
DB_USER=analytics_user
DB_PASSWORD=your_password
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend `.env` (in frontend/)

```env
VITE_API_URL=http://127.0.0.1:8001/api
```

## Database Schema Notes

- `Organization` - multi-tenant root, all data scoped to org
- `UserProfile` - extends Django User with org, role (admin/manager/viewer)
- `Transaction` - core data model with supplier/category FKs, amount, date
- `DataUpload` - tracks CSV upload history with batch_id

## Creating Admin Users

```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Then in Django shell, create profile:
docker-compose exec backend python manage.py shell
>>> from apps.authentication.models import Organization, UserProfile
>>> from django.contrib.auth.models import User
>>> org = Organization.objects.create(name='Default Org', slug='default')
>>> user = User.objects.get(username='admin')
>>> UserProfile.objects.create(user=user, organization=org, role='admin', is_active=True)
```

## Common Issues

**Login 403/500 errors:** User needs a UserProfile with organization and active status.

**Frontend changes not reflecting:** Run `docker-compose up -d --build --force-recreate frontend`

**Static files missing in admin:** Run `collectstatic` command.

**Port 8001 in use:** Check for WSL relay processes; can change in docker-compose.yml.
