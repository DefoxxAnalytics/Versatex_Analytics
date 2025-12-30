# Versatex Analytics

[![CI](https://github.com/DefoxxAnalytics/Versatex_Analytics/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/DefoxxAnalytics/Versatex_Analytics/actions/workflows/ci.yml)
[![Deploy](https://github.com/DefoxxAnalytics/Versatex_Analytics/actions/workflows/deploy.yml/badge.svg)](https://github.com/DefoxxAnalytics/Versatex_Analytics/actions/workflows/deploy.yml)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Django 5.0](https://img.shields.io/badge/Django-5.0-green.svg)](https://docs.djangoproject.com/en/5.0/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38bdf8.svg)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://www.docker.com/)
[![Railway](https://img.shields.io/badge/Railway-Deployable-0B0D0E.svg)](https://railway.app/)

> Enterprise-grade procurement analytics platform with organization-based multi-tenancy, real-time insights, and comprehensive spend analysis.

---

## Overview

Versatex Analytics is a full-stack procurement analytics dashboard designed for organizations to gain actionable insights from their spending data. Built with modern technologies and security best practices, it provides powerful analytics capabilities while maintaining data isolation across multiple tenants.

## Architecture

| Layer | Technology |
|-------|------------|
| **Backend** | Django 5.0 + Django REST Framework + PostgreSQL |
| **Frontend** | React 18 + TypeScript + Tailwind CSS 4 + Vite |
| **Authentication** | JWT tokens with role-based access control |
| **Database** | PostgreSQL with organization isolation |
| **Task Queue** | Celery + Redis for background jobs |
| **Deployment** | Docker + Docker Compose / Railway |

## Features

### Authentication & Authorization
- User registration and login with JWT token authentication
- Organization-based multi-tenancy with complete data isolation
- Role-based permissions (Admin, Manager, Viewer)
- Audit logging for compliance and security
- Custom branded admin panel with Versatex theming

### Data Management
- CSV upload with intelligent duplicate detection
- Bulk operations (delete, export)
- Supplier and category management
- Transaction CRUD operations with validation
- Upload history tracking with batch management

### Analytics Suite
| Analysis Type | Description |
|--------------|-------------|
| **Overview** | Key metrics and statistics at a glance |
| **Spend by Category/Supplier** | Breakdown of spending patterns |
| **Monthly Trends** | Time-series analysis of procurement |
| **Pareto Analysis** | 80/20 rule identification |
| **Tail Spend** | Low-value transaction identification |
| **Spend Stratification** | Kraljic Matrix classification |
| **Seasonality** | Pattern detection across periods |
| **Year-over-Year** | Comparative analysis |
| **Consolidation** | Supplier optimization opportunities |

### Security Features
- Argon2 password hashing
- JWT token authentication with refresh
- CORS protection with strict origin validation
- SQL injection and XSS protection
- CSRF protection
- Rate limiting
- HTTPS enforcement (production)
- UUID-based resource identifiers (IDOR protection)
- Failed login tracking with IP lockout

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11+ and Node.js 22+ for local development

### 1. Clone and Setup

```bash
git clone https://github.com/DefoxxAnalytics/Versatex_Analytics.git
cd Versatex_Analytics

# Copy environment variables
cp .env.example .env

# Edit .env and set your configuration
nano .env
```

### 2. Start with Docker

```bash
# Build and start all services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Services available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8001/api
# - Django Admin: http://localhost:8001/admin
# - API Docs: http://localhost:8001/api/docs
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Create initial organization
docker-compose exec backend python manage.py shell
>>> from apps.authentication.models import Organization
>>> org = Organization.objects.create(name="My Company", slug="my-company")
>>> exit()
```

### 4. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application |
| Django Admin | http://localhost:8001/admin | Administration panel |
| API Docs | http://localhost:8001/api/docs | Interactive API documentation |

## API Reference

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register/` | POST | Register new user |
| `/api/v1/auth/login/` | POST | Login |
| `/api/v1/auth/logout/` | POST | Logout |
| `/api/v1/auth/token/refresh/` | POST | Refresh JWT token |
| `/api/v1/auth/user/` | GET | Get current user |
| `/api/v1/auth/change-password/` | POST | Change password |

### Procurement
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/procurement/suppliers/` | GET/POST | List/create suppliers |
| `/api/v1/procurement/categories/` | GET/POST | List/create categories |
| `/api/v1/procurement/transactions/` | GET/POST | List/create transactions |
| `/api/v1/procurement/transactions/upload_csv/` | POST | Upload CSV data |
| `/api/v1/procurement/transactions/bulk_delete/` | POST | Bulk delete |
| `/api/v1/procurement/transactions/export/` | GET | Export to CSV |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analytics/overview/` | GET | Overview statistics |
| `/api/v1/analytics/spend-by-category/` | GET | Spend by category |
| `/api/v1/analytics/spend-by-supplier/` | GET | Spend by supplier |
| `/api/v1/analytics/monthly-trend/` | GET | Monthly trend |
| `/api/v1/analytics/pareto/` | GET | Pareto analysis |
| `/api/v1/analytics/tail-spend/` | GET | Tail spend analysis |
| `/api/v1/analytics/stratification/` | GET | Spend stratification |
| `/api/v1/analytics/seasonality/` | GET | Seasonality analysis |
| `/api/v1/analytics/year-over-year/` | GET | Year over year |
| `/api/v1/analytics/consolidation/` | GET | Consolidation opportunities |

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Type checking
pnpm check

# Build for production
pnpm build
```

### Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
pnpm test        # Watch mode
pnpm test:run    # Single run
pnpm test:ui     # With UI
```

## Database Schema

### Core Models

| Model | Description |
|-------|-------------|
| **Organization** | Multi-tenant root with isolated data |
| **User/UserProfile** | Extended Django User with org, role |
| **Supplier** | Vendor information |
| **Category** | Spend categories (hierarchical) |
| **Transaction** | Procurement transactions |
| **DataUpload** | Upload history tracking |

### User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, user management, bulk delete, Django Admin |
| **Manager** | Upload data, manage own data |
| **Viewer** | Read-only access |

## Deployment

### Railway (Recommended)

Railway provides native support for the full stack with minimal configuration.

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy
railway up
```

**Cost Estimate:**
- Development: ~$15-20/month
- Production: ~$40-50/month

See [Railway Step-by-Step Guide](docs/deployment/RAILWAY-STEP-BY-STEP.md) for detailed instructions.

### Docker Compose (Self-Hosted)

```bash
# Production deployment
docker-compose --profile production up -d

# With custom port
FRONTEND_PORT=8080 docker-compose up -d
```

## CSV Upload Format

### Required Columns
| Column | Description |
|--------|-------------|
| `supplier` | Supplier name |
| `category` | Category name |
| `amount` | Transaction amount |
| `date` | Transaction date (YYYY-MM-DD) |

### Optional Columns
| Column | Description |
|--------|-------------|
| `description` | Transaction description |
| `subcategory` | Subcategory |
| `location` | Location |
| `fiscal_year` | Fiscal year |
| `spend_band` | Spend band |
| `payment_method` | Payment method |
| `invoice_number` | Invoice number |

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/setup/QUICK_START_GUIDE.md) | Fast setup for development |
| [Windows Setup](docs/setup/WINDOWS-SETUP.md) | Windows-specific instructions |
| [Docker Troubleshooting](docs/setup/DOCKER-TROUBLESHOOTING.md) | Common issues and solutions |
| [Railway Deployment](docs/deployment/RAILWAY-STEP-BY-STEP.md) | Production deployment guide |
| [Development Guide](docs/development/CLAUDE.md) | AI assistant guidelines |

## Troubleshooting

### Database Connection Issues
```bash
docker-compose ps db
docker-compose logs db
docker-compose restart db
```

### Backend Issues
```bash
docker-compose logs backend
docker-compose restart backend
docker-compose exec backend python manage.py migrate
```

### Frontend Issues
```bash
docker-compose logs frontend
docker-compose up -d --build frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - All rights reserved. See [LICENSE](LICENSE) for details.

## Credits

Built with Django, React, PostgreSQL, and Docker by [Defoxx Analytics](https://github.com/DefoxxAnalytics).

---

<p align="center">
  <sub>Made with care by the Versatex team</sub>
</p>
