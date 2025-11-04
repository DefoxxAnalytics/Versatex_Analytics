# Analytics Dashboard - Full Stack Application

Complete procurement analytics dashboard with Django backend, React frontend, and organization-based multi-tenancy.

## 🏗️ Architecture

- **Backend**: Django 5.0 + Django REST Framework + PostgreSQL
- **Frontend**: React 19 + TypeScript + Tailwind CSS
- **Authentication**: JWT tokens with role-based access control
- **Database**: PostgreSQL with organization isolation
- **Task Queue**: Celery + Redis for background jobs
- **Deployment**: Docker + Docker Compose

## 🎯 Features

### Authentication & Authorization
- ✅ User registration and login
- ✅ JWT token authentication with refresh
- ✅ Organization-based multi-tenancy
- ✅ 3 roles: Admin, Manager, Viewer
- ✅ Role-based permissions
- ✅ Audit logging
- ✅ Custom branded admin panel (Navy blue theme with Versatex branding)
- ✅ Admin-only features (Django Admin Panel access via Shield icon)

### Data Management
- ✅ CSV upload with duplicate detection
- ✅ Bulk delete transactions
- ✅ Export to CSV
- ✅ Supplier and category management
- ✅ Transaction CRUD operations
- ✅ Upload history tracking

### Analytics
- ✅ Overview statistics
- ✅ Spend by category and supplier
- ✅ Monthly trend analysis
- ✅ Pareto analysis (80/20 rule)
- ✅ Tail spend identification
- ✅ Spend stratification (Kraljic Matrix)
- ✅ Seasonality patterns
- ✅ Year-over-year comparison
- ✅ Supplier consolidation opportunities

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11+ and Node.js 22+ for local development

### 1. Clone and Setup

```bash
# Extract the project
tar -xzf analytics-dashboard-fullstack.tar.gz
cd analytics-dashboard-fullstack

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

# The services will be available at:
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

# Create initial organization (optional)
docker-compose exec backend python manage.py shell
>>> from apps.authentication.models import Organization
>>> org = Organization.objects.create(name="My Company", slug="my-company")
>>> exit()
```

### 4. Access the Application

1. **Frontend**: http://localhost:3000
   - Login with the superuser credentials you created
   - Admin users will see a "Admin Panel" link (with Shield icon) in the sidebar
2. **Django Admin**: http://localhost:8001/admin
   - Custom branded navy blue theme with Versatex logo
   - Timezone set to EST (America/New_York)
3. **API Documentation**: http://localhost:8001/api/docs

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/user/` - Get current user
- `POST /api/auth/change-password/` - Change password

### Procurement
- `GET /api/procurement/suppliers/` - List suppliers
- `GET /api/procurement/categories/` - List categories
- `GET /api/procurement/transactions/` - List transactions
- `POST /api/procurement/transactions/upload_csv/` - Upload CSV
- `POST /api/procurement/transactions/bulk_delete/` - Bulk delete
- `GET /api/procurement/transactions/export/` - Export to CSV

### Analytics
- `GET /api/analytics/overview/` - Overview statistics
- `GET /api/analytics/spend-by-category/` - Spend by category
- `GET /api/analytics/spend-by-supplier/` - Spend by supplier
- `GET /api/analytics/monthly-trend/` - Monthly trend
- `GET /api/analytics/pareto/` - Pareto analysis
- `GET /api/analytics/tail-spend/` - Tail spend analysis
- `GET /api/analytics/stratification/` - Spend stratification
- `GET /api/analytics/seasonality/` - Seasonality analysis
- `GET /api/analytics/year-over-year/` - Year over year
- `GET /api/analytics/consolidation/` - Consolidation opportunities

## 🔧 Development

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

# Build for production
pnpm build
```

## 📊 Database Schema

### Organizations
- Multi-tenant architecture
- Each organization has isolated data

### Users & Roles
- **Admin**: Full access, user management, bulk delete, Django Admin Panel access
- **Manager**: Upload data, manage own data
- **Viewer**: Read-only access

Note: Only users with `profile.role === 'admin'` can see and access the Django Admin Panel link in the frontend sidebar.

### Procurement Data
- **Suppliers**: Vendor information
- **Categories**: Spend categories
- **Transactions**: Procurement transactions
- **DataUploads**: Upload history

## 🔐 Security

- Argon2 password hashing
- JWT token authentication
- CORS protection
- SQL injection protection
- XSS protection
- CSRF protection
- Rate limiting (production)
- HTTPS enforcement (production)

## 📦 Deployment

### Docker Compose (Recommended)

```bash
# Production deployment
docker-compose --profile production up -d

# With custom port
FRONTEND_PORT=8080 docker-compose up -d
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### DigitalOcean

See `docs/DEPLOYMENT-DIGITALOCEAN.md` for detailed instructions.

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
pnpm test
```

## 📝 CSV Upload Format

Required columns:
- `supplier` - Supplier name
- `category` - Category name
- `amount` - Transaction amount
- `date` - Transaction date (YYYY-MM-DD)

Optional columns:
- `description` - Transaction description
- `subcategory` - Subcategory
- `location` - Location
- `fiscal_year` - Fiscal year
- `spend_band` - Spend band
- `payment_method` - Payment method
- `invoice_number` - Invoice number

## 🛠️ Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Backend Issues
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Run migrations
docker-compose exec backend python manage.py migrate
```

### Frontend Issues
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

## 📖 Documentation

### Essential Guides
- [Quick Start Guide](docs/setup/QUICK_START_GUIDE.md) - Fast setup for development
- [Windows Setup](docs/setup/WINDOWS-SETUP.md) - Windows-specific instructions
- [Docker Troubleshooting](docs/setup/DOCKER-TROUBLESHOOTING.md) - Common issues and solutions
- [Development Guide](docs/development/CLAUDE.md) - AI assistant guidelines for this codebase

### Interactive Documentation
- [API Documentation](http://localhost:8001/api/docs) - Interactive API docs
- [Django Admin](http://localhost:8001/admin) - Custom branded admin interface

### More Documentation
See the [docs/](docs/) directory for all documentation organized by category.

## 🎨 Customizations

### Django Admin Panel
- **Custom Branding**: Navy blue theme (#1e3a8a) with Versatex logo
- **Custom Templates**:
  - `templates/admin/login.html` - Branded login page with centered card design
  - `templates/admin/base_site.html` - Custom header with logo and navy blue theme
  - `templates/admin/index.html` - Custom dashboard with welcome banner
- **Timezone**: Set to EST (America/New_York) for all admin timestamps
- **Logout Behavior**: Redirects to admin login page instead of default

### Frontend
- **Login Page**: Versatex logo displayed prominently (replaced Lock icon)
- **Admin Access**: Shield icon link to Django Admin Panel (visible only to admin users)
- **Port Configuration**: Backend runs on port 8001 to avoid conflicts

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check Docker logs
4. Contact support

## 📄 License

Proprietary - All rights reserved

## 🎉 Credits

Built with Django, React, PostgreSQL, and Docker.
