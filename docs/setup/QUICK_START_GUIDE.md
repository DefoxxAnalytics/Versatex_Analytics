# Analytics Dashboard - Quick Start Guide

This guide will help you get the Analytics Dashboard up and running in under 10 minutes.

## Prerequisites

- **Docker Desktop** installed and running
- **Git** (if cloning from repository)
- At least **4GB of free RAM**
- Ports **3000**, **8001**, **5432**, and **6379** available

## Step 1: Get the Project

```bash
# If you have the tar.gz file
tar -xzf analytics-dashboard-fullstack.tar.gz
cd analytics-dashboard-fullstack-7

# OR if cloning from git
git clone <repository-url>
cd analytics-dashboard-fullstack-7
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred text editor
# At minimum, change these values:
# - POSTGRES_PASSWORD (set a secure password)
# - SECRET_KEY (generate a random string)
# - JWT_SECRET_KEY (generate a different random string)
```

**Quick environment setup (optional):**
```bash
# Generate secure keys
# On Linux/Mac:
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)

# Update .env file with these values
```

## Step 3: Start Docker Containers

```bash
# Build and start all services
docker-compose up -d --build

# This will start:
# - PostgreSQL database (port 5432)
# - Redis (port 6379)
# - Django backend (port 8001)
# - Celery worker
# - React frontend (port 3000)
```

**Check if services are running:**
```bash
docker-compose ps

# All services should show "Up" status
```

## Step 4: Initialize Database

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sessions, ...
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   ...
```

## Step 5: Create Admin User

```bash
# Create superuser account
docker-compose exec backend python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: admin@example.com
# Password: [choose a secure password]
# Password (again): [repeat password]
```

## Step 6: Create Organization and Profile

```bash
# Open Django shell
docker-compose exec backend python manage.py shell

# Then run these commands:
```

```python
from apps.authentication.models import Organization, UserProfile
from django.contrib.auth.models import User

# Get the admin user
admin = User.objects.get(username='admin')

# Create organization
org = Organization.objects.create(
    name='Default Organization',
    slug='default'
)

# Create admin profile
profile = UserProfile.objects.create(
    user=admin,
    organization=org,
    role='admin',
    is_active=True
)

# Verify
print(f"Created profile for {admin.username} with role {profile.role}")

# Exit
exit()
```

## Step 7: Collect Static Files (for Admin Panel)

```bash
# Collect static files for Django Admin
docker-compose exec backend python manage.py collectstatic --noinput

# You should see:
# Copying static files...
# X static files copied to '/app/staticfiles'
```

## Step 8: Access the Application

Open your browser and navigate to:

### Frontend Application
**URL:** http://localhost:3000

1. Click "Sign In" on the login page
2. Enter your admin credentials:
   - Username: `admin`
   - Password: [the password you created]
3. You should see the dashboard overview

**Admin users will see:**
- A **Shield icon** labeled "Admin Panel" in the sidebar
- This link opens the Django Admin Panel in a new tab

### Django Admin Panel
**URL:** http://localhost:8001/admin

1. Navigate to http://localhost:8001/admin
2. You'll see a custom branded login page with:
   - Navy blue theme
   - Versatex logo
   - "Analytics Dashboard" header
3. Login with your admin credentials
4. Explore the admin interface

### API Documentation
**URL:** http://localhost:8001/api/docs

Interactive Swagger API documentation for developers.

## Step 9: Upload Data (Optional)

1. In the frontend (http://localhost:3000), click "Upload Data" in the sidebar
2. Download the sample CSV template
3. Prepare your procurement data with these required columns:
   - `supplier` - Supplier name
   - `category` - Category name
   - `amount` - Transaction amount
   - `date` - Transaction date (YYYY-MM-DD)
4. Upload your CSV file
5. Navigate to other tabs to see analytics

## Verify Everything Works

### Check Frontend
- ✅ Login page shows Versatex logo (not a Lock icon)
- ✅ Can login successfully
- ✅ Dashboard loads without errors
- ✅ Admin users see "Admin Panel" link with Shield icon

### Check Backend API
```bash
# Test API health
curl http://localhost:8001/api/

# Should return API information
```

### Check Django Admin
- ✅ Admin login page has navy blue theme
- ✅ Versatex logo is visible
- ✅ Can login successfully
- ✅ Dashboard shows welcome message
- ✅ Times are displayed in EST

### Check Logs
```bash
# View all service logs
docker-compose logs -f

# Or specific services
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Quick Troubleshooting

### Port 8001 Already in Use
```bash
# Check what's using port 8001
# Windows:
netstat -ano | findstr :8001

# Linux/Mac:
lsof -i :8001

# Kill the process or change the port in docker-compose.yml
```

### Can't Login - 403 Error
```bash
# Check backend logs
docker-compose logs backend | tail -50

# Restart backend
docker-compose restart backend
```

### Can't Login - 500 Error
This usually means the user profile wasn't created. Repeat Step 6.

### Logo Not Showing in Admin Panel
```bash
# Recollect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Restart backend
docker-compose restart backend

# Clear browser cache (Ctrl+Shift+R)
```

### Changes Not Showing in Frontend
```bash
# Force rebuild frontend
docker-compose up -d --build --force-recreate frontend
```

### Database Connection Error
```bash
# Check if database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

## Stopping the Application

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including volumes (DELETES DATA)
docker-compose down -v
```

## Restarting After Stopping

```bash
# Start services (no rebuild needed)
docker-compose up -d

# Start with logs visible
docker-compose up
```

## Key Features to Explore

### For Admin Users
1. **Django Admin Panel** - Full CRUD operations on all models
2. **User Management** - Create and manage users, roles, organizations
3. **Bulk Delete** - Delete multiple transactions at once
4. **Audit Logs** - View recent actions in admin panel

### For All Users
1. **Upload Data** - CSV upload with duplicate detection
2. **Overview** - Key metrics and KPIs
3. **Categories** - Spend analysis by category
4. **Suppliers** - Supplier performance
5. **Pareto Analysis** - 80/20 rule insights
6. **Spend Stratification** - Kraljic Matrix
7. **Seasonality** - Time-based patterns
8. **Year-over-Year** - Trend comparison
9. **Tail Spend** - Long-tail analysis
10. **AI Insights** - Smart recommendations
11. **Predictive Analytics** - Forecasting
12. **Contract Optimization** - Contract analysis
13. **Maverick Spend** - Policy compliance

## User Roles

### Admin Role
- Full access to all features
- Can access Django Admin Panel (Shield icon in sidebar)
- Can create/edit/delete users
- Can bulk delete transactions
- Can manage organizations

### Manager Role
- Can upload procurement data
- Can view all analytics
- Can export data
- Cannot access Django Admin Panel
- Cannot bulk delete

### Viewer Role
- Can view all analytics
- Can apply filters
- Cannot upload data
- Cannot modify data
- Cannot access Django Admin Panel

## Creating Additional Users

### Via Django Admin Panel (Recommended for Admins)

1. Navigate to http://localhost:8001/admin
2. Click "Users" under "AUTHENTICATION AND AUTHORIZATION"
3. Click "Add User" button
4. Fill in username and password
5. Click "Save and continue editing"
6. Scroll down to "User profiles" section
7. Click "Add another User profile"
8. Select organization and role
9. Check "Is active"
10. Click "Save"

### Via Django Shell (For Developers)

```bash
docker-compose exec backend python manage.py shell
```

```python
from django.contrib.auth.models import User
from apps.authentication.models import Organization, UserProfile

# Create user
user = User.objects.create_user(
    username='manager1',
    email='manager1@example.com',
    password='secure_password'
)

# Get organization
org = Organization.objects.get(slug='default')

# Create profile
profile = UserProfile.objects.create(
    user=user,
    organization=org,
    role='manager',  # or 'viewer'
    is_active=True
)

print(f"Created {user.username} with role {profile.role}")
exit()
```

## Next Steps

1. **Upload your procurement data** using the CSV upload feature
2. **Explore the analytics tabs** to gain insights
3. **Create additional users** with different roles to test permissions
4. **Customize the admin panel** further if needed
5. **Review the full documentation** in README.md and CLAUDE.md

## Getting Help

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Check Service Status
```bash
docker-compose ps
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Access Service Shell
```bash
# Backend Python shell
docker-compose exec backend python manage.py shell

# Backend bash shell
docker-compose exec backend bash

# Database shell
docker-compose exec db psql -U analytics_user -d analytics_db
```

## Important URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/api
- **Django Admin:** http://localhost:8001/admin
- **API Docs:** http://localhost:8001/api/docs

## Configuration Files

- `.env` - Environment variables
- `docker-compose.yml` - Docker service configuration
- `backend/config/settings.py` - Django settings
- `frontend/.env` - Frontend environment variables

## Customization

The application has been customized with:
- **Navy blue color scheme** (#1e3a8a) throughout Django Admin
- **Versatex logo** on login pages (frontend and admin)
- **EST timezone** for admin panel timestamps
- **Admin-only features** (Shield icon link to admin panel)
- **Custom admin templates** in `backend/templates/admin/`

For more details on customizations, see [CLAUDE.md](CLAUDE.md).

## Success Checklist

- [ ] All containers are running (`docker-compose ps`)
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] Organization and profile created
- [ ] Static files collected
- [ ] Can access frontend at http://localhost:3000
- [ ] Can login to frontend
- [ ] Can access Django admin at http://localhost:8001/admin
- [ ] Admin users see "Admin Panel" link in sidebar
- [ ] Logo shows on both login pages
- [ ] Can upload CSV data
- [ ] Analytics charts display correctly

If all boxes are checked, you're ready to use the Analytics Dashboard!

## Support

For detailed technical documentation, see:
- [README.md](README.md) - General overview
- [CLAUDE.md](CLAUDE.md) - Development guide with troubleshooting

For issues:
1. Check the troubleshooting section above
2. Review Docker logs
3. Verify all services are running
4. Check environment configuration
