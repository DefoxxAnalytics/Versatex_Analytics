# Versatex Analytics - Development Guide

This document provides detailed technical information for developers working on Versatex Analytics.

## Project Structure

```
analytics-dashboard-fullstack-7/
├── backend/
│   ├── apps/
│   │   ├── analytics/          # Analytics endpoints and calculations
│   │   ├── authentication/     # Auth, users, organizations, profiles
│   │   └── procurement/        # Suppliers, categories, transactions
│   ├── config/                 # Django settings and URLs
│   ├── templates/              # Custom Django admin templates
│   │   └── admin/
│   │       ├── base_site.html  # Custom admin base (navy theme, logo)
│   │       ├── login.html      # Custom admin login (branded)
│   │       └── index.html      # Custom admin dashboard
│   ├── static/                 # Static files (logos, etc.)
│   │   └── vtx_logo2.png
│   ├── staticfiles/            # Collected static files (generated)
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── DashboardLayout.tsx  # Main layout with sidebar (Admin Panel link)
│   │   │   ├── FilterPane.tsx
│   │   │   └── Breadcrumb.tsx
│   │   ├── contexts/           # React contexts (AuthContext)
│   │   ├── hooks/              # Custom hooks
│   │   ├── lib/                # Utilities (api.ts, utils.ts)
│   │   ├── pages/              # Page components
│   │   │   ├── Login.tsx       # Login page with Versatex logo
│   │   │   ├── Overview.tsx
│   │   │   └── ...
│   │   └── App.tsx
│   ├── public/
│   │   └── vtx_logo2.png       # Versatex logo
│   └── package.json
├── docker-compose.yml
├── .env
└── README.md
```

## Key Customizations

### 1. Port Configuration

**Backend runs on port 8001** (not 8000) to avoid conflicts with WSL relay processes.

**Files changed:**
- `docker-compose.yml`: Backend service port mapping `8001:8000`
- `frontend/.env`: `VITE_API_URL=http://127.0.0.1:8001/api`

### 2. Django Admin Panel Customization

#### Custom Templates (`backend/templates/admin/`)

**base_site.html**
- Navy blue header (#1e3a8a)
- Versatex logo in header (white inverted)
- Changed title to "Analytics Dashboard Admin Panel"
- Custom footer with copyright notice
- CSS variables for theme colors

**login.html**
- Navy blue background (#1e3a8a)
- Centered white card design with rounded corners
- Versatex logo at top of card
- Branded header "Analytics Dashboard" and "Admin Panel Login"
- No sidebar/collapse functionality
- Custom error styling with red borders

**index.html**
- Navy blue welcome banner
- Enhanced welcome message
- Custom module styling with hover effects
- Uses `{{ block.super }}` to render Django's default app list

#### Settings Changes (`backend/config/settings.py`)

```python
# Custom templates directory
TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],  # Added
        # ...
    }
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # For vtx_logo2.png
]

# Admin logout redirect
LOGOUT_REDIRECT_URL = '/admin/login/'

# Timezone
TIME_ZONE = 'America/New_York'  # EST/EDT

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8080',
]
```

#### Collecting Static Files

After any changes to `backend/static/`:
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

### 3. Frontend Customizations

#### Admin Panel Access (`frontend/src/components/DashboardLayout.tsx`)

**isAdmin() Helper Function**
```typescript
function isAdmin(): boolean {
  try {
    const userStr = localStorage.getItem('user');
    if (!userStr) return false;

    const user = JSON.parse(userStr);
    return user?.profile?.role === 'admin';
  } catch {
    return false;
  }
}
```

**Admin Panel Link in Sidebar**
- Rendered before Settings item
- Uses Shield icon from lucide-react
- Opens `http://localhost:8001/admin/` in new tab
- Only visible when `isAdmin() === true`

```typescript
// In navigation rendering
if (item.path === '/settings' && isAdmin()) {
  return (
    <div key="admin-section">
      <a
        href={`${window.location.protocol}//${window.location.hostname}:8001/admin/`}
        target="_blank"
        rel="noopener noreferrer"
        title="Django Admin Panel (admins only)"
      >
        <Shield className="h-5 w-5 text-gray-500" />
        <span className="text-sm">Admin Panel</span>
      </a>
      <Link href="/settings">
        <Settings />
        <span>Settings</span>
      </Link>
    </div>
  );
}
```

#### Login Page (`frontend/src/pages/Login.tsx`)

**Versatex Logo Integration**
```typescript
<CardHeader className="space-y-4 pb-8">
  <div className="flex justify-center">
    <img
      src="/vtx_logo2.png"
      alt="Versatex Logo"
      className="h-24 w-auto"
    />
  </div>
  <div className="text-center">
    <CardTitle className="text-3xl font-bold">
      Analytics Dashboard
    </CardTitle>
    <CardDescription>
      Sign in to access your procurement analytics
    </CardDescription>
  </div>
</CardHeader>
```

**Login Fix - State Update Timing**
```typescript
// After successful login
toast.success('Login successful');
checkAuth();

// Delay navigation to allow state updates
setTimeout(() => {
  setLocation('/');
}, 100);
```

### 4. Authentication Flow

#### Backend (`backend/apps/authentication/views.py`)

**CSRF Exemption for LoginView**
```python
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    # ...
```

**User Profile Validation**
```python
# Check for active profile
if not hasattr(user, 'profile') or not user.profile.is_active:
    return Response(
        {'error': 'User profile is inactive'},
        status=status.HTTP_403_FORBIDDEN
    )
```

### 5. User Roles and Permissions

**Role Hierarchy:**
1. **admin**: Full access + Django Admin Panel + bulk delete
2. **manager**: Upload data, manage own data
3. **viewer**: Read-only access

**Creating Admin User:**
```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Create organization and profile (Django shell)
docker-compose exec backend python manage.py shell
>>> from apps.authentication.models import Organization, UserProfile
>>> from django.contrib.auth.models import User
>>>
>>> # Get the admin user
>>> admin = User.objects.get(username='admin')
>>>
>>> # Create organization
>>> org = Organization.objects.create(name='Default Organization', slug='default')
>>>
>>> # Create profile with admin role
>>> profile = UserProfile.objects.create(
...     user=admin,
...     organization=org,
...     role='admin',
...     is_active=True
... )
>>> exit()
```

## Common Tasks

### Rebuilding Frontend

If frontend changes aren't reflected (cached builds):
```bash
# Force complete rebuild
docker-compose up -d --build --force-recreate frontend

# Or with down first
docker-compose down
docker-compose up -d --build
```

### Database Migrations

```bash
# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate

# Check migration status
docker-compose exec backend python manage.py showmigrations
```

### Logs and Debugging

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50 backend
```

### Port Conflicts

If ports are in use:
```bash
# Check what's using port 8001 (Windows)
netstat -ano | findstr :8001

# Check what's using port 8001 (Linux/Mac)
lsof -i :8001

# Change backend port in docker-compose.yml
backend:
  ports:
    - "8002:8000"  # Use different external port

# Update frontend/.env
VITE_API_URL=http://127.0.0.1:8002/api

# Rebuild frontend
docker-compose up -d --build frontend
```

## Environment Variables

### Backend (.env)

```bash
# Database
POSTGRES_DB=analytics_db
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:3000,http://localhost:5173

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

### Frontend (.env)

```bash
VITE_API_URL=http://127.0.0.1:8001/api
```

## Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend python manage.py test

# Run specific app tests
docker-compose exec backend python manage.py test apps.authentication
docker-compose exec backend python manage.py test apps.procurement

# With coverage
docker-compose exec backend coverage run --source='.' manage.py test
docker-compose exec backend coverage report
```

### Frontend Tests

```bash
# Run tests
docker-compose exec frontend pnpm test

# Run with coverage
docker-compose exec frontend pnpm test --coverage
```

## Color Scheme

**Primary Navy Blue:** `#1e3a8a`
**Hover Navy Blue:** `#1e40af`

Used in:
- Django Admin header
- Django Admin login background
- Django Admin buttons
- Admin module headers
- Links and accents

## Logo Assets

**Location:**
- Frontend: `frontend/public/vtx_logo2.png`
- Backend: `backend/static/vtx_logo2.png`

**Usage:**
- Frontend login page (h-24 w-auto)
- Django admin login (max-width: 180px, inverted white)
- Django admin header (40x40px, inverted white)

## API Authentication

All API requests (except login/register) require JWT token:

```typescript
// In frontend/src/lib/api.ts
const token = localStorage.getItem('access_token');
if (token) {
  config.headers.Authorization = `Bearer ${token}`;
}
```

**Token Refresh:**
```typescript
// When 401 received
const refreshToken = localStorage.getItem('refresh_token');
const response = await axios.post('/api/auth/token/refresh/', {
  refresh: refreshToken
});
localStorage.setItem('access_token', response.data.access);
```

## Timezone Handling

**Backend Timezone:** America/New_York (EST/EDT)
- All timestamps in Django Admin show in EST
- Database stores in UTC
- Automatic conversion for display

**Frontend Timezone:**
- Browser local timezone for charts
- Use `toLocaleString()` for user display

## Troubleshooting

### Issue: 403 Forbidden on Login

**Cause:** CSRF/CORS misconfiguration

**Fix:**
1. Check `CSRF_TRUSTED_ORIGINS` in settings.py
2. Verify `@csrf_exempt` on LoginView
3. Check `CORS_ALLOWED_ORIGINS` matches frontend URL

### Issue: 500 Error on Login

**Cause:** User has no UserProfile

**Fix:**
```bash
docker-compose exec backend python manage.py shell
>>> from apps.authentication.models import Organization, UserProfile
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> org = Organization.objects.first() or Organization.objects.create(name='Default Org', slug='default')
>>> UserProfile.objects.create(user=user, organization=org, role='admin', is_active=True)
```

### Issue: Login Redirect Loop

**Cause:** React state not updating before navigation

**Fix:** Already implemented with `setTimeout(100)` in Login.tsx

### Issue: Admin Panel Link Not Showing

**Cause:** User role is not 'admin'

**Check:**
```bash
docker-compose exec backend python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.profile.role  # Should be 'admin'
>>> user.profile.role = 'admin'
>>> user.profile.save()
```

### Issue: Logo Not Showing in Admin Panel

**Cause:** Static files not collected

**Fix:**
```bash
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose restart backend
```

### Issue: Frontend Changes Not Reflected

**Cause:** Vite build cache

**Fix:**
```bash
docker-compose up -d --build --force-recreate frontend
```

## Development Tips

1. **Use Context7** for checking up-to-date docs when implementing new libraries or frameworks
2. **Always test both admin and non-admin users** when making role-based UI changes
3. **Run `collectstatic` after modifying** `backend/static/` files
4. **Force frontend rebuild** if logo/image changes aren't showing
5. **Check both ports** (3000 for frontend, 8001 for backend) when testing
6. **Clear browser cache** if styles aren't updating in Django Admin
7. **Use Docker logs** to debug authentication issues

## Next Steps

- Add more comprehensive tests
- Implement email notifications for admins
- Add audit logging UI in admin panel
- Enhance role permissions with more granular controls
- Add user management UI in frontend for admins
