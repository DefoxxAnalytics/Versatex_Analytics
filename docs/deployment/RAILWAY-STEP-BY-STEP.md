# Complete Step-by-Step Railway Deployment Guide

**Detailed walkthrough for deploying the Analytics Dashboard to Railway from scratch.**

---

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Part 1: Account Setup](#part-1-account-setup)
3. [Part 2: Create Railway Project](#part-2-create-railway-project)
4. [Part 3: Deploy Database Services](#part-3-deploy-database-services)
5. [Part 4: Deploy Backend Service](#part-4-deploy-backend-service)
6. [Part 5: Deploy Celery Worker](#part-5-deploy-celery-worker)
7. [Part 6: Deploy Frontend Service](#part-6-deploy-frontend-service)
8. [Part 7: Initialize Database](#part-7-initialize-database)
9. [Part 8: Create Admin User](#part-8-create-admin-user)
10. [Part 9: Test Your Deployment](#part-9-test-your-deployment)
11. [Part 10: Custom Domain Setup](#part-10-custom-domain-setup-optional)
12. [Part 11: Enable Auto-Deploy](#part-11-enable-auto-deploy)
13. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Before You Begin

### What You'll Need

- ✅ GitHub account with your code repository
- ✅ Railway account (sign up at [railway.app](https://railway.app))
- ✅ Credit card (for Railway - they don't charge until you exceed $5 usage)
- ✅ 30-45 minutes of time

### Your Repository

Ensure your code is pushed to GitHub at:
```
https://github.com/DefoxxAnalytics/Refactoring_vstx-analytics-dashboard-v2
```

All necessary files are already committed:
- ✅ railway.toml
- ✅ .env.production.example
- ✅ backend/Dockerfile.railway
- ✅ frontend/Dockerfile.railway
- ✅ docker-compose.yml

---

## Part 1: Account Setup

### Step 1.1: Create Railway Account

1. **Go to Railway**: https://railway.app
2. **Click "Start a New Project" or "Login"**
3. **Sign up with GitHub** (recommended):
   - Click "Login with GitHub"
   - Authorize Railway to access your GitHub account
   - This enables automatic deployments from your repo

4. **Add Payment Method**:
   - Go to Account Settings (top right → Settings)
   - Click "Billing"
   - Add credit card
   - Railway gives you $5 free credit per month
   - You won't be charged until you exceed this amount

### Step 1.2: Install Railway CLI (Optional)

While optional, the CLI makes database operations easier:

**On Windows:**
```powershell
npm install -g @railway/cli
```

**On macOS/Linux:**
```bash
npm install -g @railway/cli
```

**Verify installation:**
```bash
railway --version
```

**Login to Railway:**
```bash
railway login
```

This will open a browser window to authenticate.

---

## Part 2: Create Railway Project

### Step 2.1: Create New Project

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "+ New Project"** (big button in the center or top right)
3. **You'll see several options**:
   - Deploy from GitHub repo
   - Start with a template
   - Empty project

4. **Select "Empty Project"** for now
   - This gives us more control over the setup
   - Name it: `analytics-dashboard-production`

### Step 2.2: Project Settings

1. **Click on your new project** to open it
2. **You'll see an empty canvas** - this is where your services will appear
3. **Note your Project ID** (in the URL: `railway.app/project/[PROJECT_ID]`)

---

## Part 3: Deploy Database Services

### Step 3.1: Add PostgreSQL Database

1. **In your project, click "+ New"** (top right)
2. **Select "Database"**
3. **Choose "Add PostgreSQL"**
4. **Railway will create the database automatically**
   - Wait 10-20 seconds for it to provision
   - A card labeled "Postgres" will appear

5. **Rename the service** (optional but recommended):
   - Click on the Postgres card
   - Click the name at the top
   - Rename to: `analytics-db`

6. **View Database Credentials**:
   - Click on the `analytics-db` card
   - Go to "Variables" tab
   - You'll see `DATABASE_URL` - Railway automatically creates this
   - **Don't copy it yet** - we'll reference it later

### Step 3.2: Add Redis Cache

1. **Click "+ New"** again
2. **Select "Database"**
3. **Choose "Add Redis"**
4. **Wait for provisioning** (10-20 seconds)
5. **Rename to**: `analytics-redis`
6. **View Redis URL**:
   - Click on `analytics-redis` card
   - Go to "Variables" tab
   - You'll see `REDIS_URL` - Railway creates this automatically

**✅ Checkpoint**: You should now see 2 service cards:
- `analytics-db` (PostgreSQL)
- `analytics-redis` (Redis)

---

## Part 4: Deploy Backend Service

### Step 4.1: Create Backend Service

1. **Click "+ New"** in your project
2. **Select "GitHub Repo"**
3. **Configure GitHub App** (if first time):
   - Click "Configure GitHub App"
   - Select your GitHub organization/account
   - Choose repository access:
     - Select "Only select repositories"
     - Choose: `Refactoring_vstx-analytics-dashboard-v2`
   - Click "Install & Authorize"

4. **Select Your Repository**:
   - You should now see your repo in the list
   - Click on: `DefoxxAnalytics/Refactoring_vstx-analytics-dashboard-v2`

5. **Railway will start deploying** - STOP IT:
   - Click the X or Cancel on the deployment
   - We need to configure it first

### Step 4.2: Configure Backend Service

1. **Rename Service**:
   - Click on the service card
   - Rename to: `backend`

2. **Set Root Directory** (if needed):
   - Click "Settings" tab
   - Scroll to "Build"
   - Root Directory: leave blank (Railway will auto-detect)
   - Check Custom Dockerfile Path: `backend/Dockerfile.railway`

3. **Configure Environment Variables**:
   - Click "Variables" tab
   - Click "+ New Variable"
   - Add these variables one by one:

```bash
# Django Core Settings
DJANGO_SETTINGS_MODULE=config.settings
DEBUG=False
PYTHONUNBUFFERED=1

# Security - Generate a new SECRET_KEY
SECRET_KEY=your-super-secret-key-here-generate-a-new-one-at-least-50-characters-long

# Database Connection - Reference the PostgreSQL service
DATABASE_URL=${{analytics-db.DATABASE_URL}}

# Redis Connection - Reference the Redis service
REDIS_URL=${{analytics-redis.REDIS_URL}}

# Celery Configuration
CELERY_BROKER_URL=${{analytics-redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{analytics-redis.REDIS_URL}}

# Timezone
TZ=America/New_York

# Allowed Hosts - We'll update this after deployment
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},.railway.app

# CORS - We'll update this after frontend is deployed
CORS_ALLOWED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}
CSRF_TRUSTED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}

# Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

**Important Notes:**

- **SECRET_KEY**: Generate a new one! Use this command locally:
  ```bash
  # Works without Django installed
  python -c "import secrets, string; chars = string.ascii_letters + string.digits + '@#$%^&*()_+-='; print(''.join(secrets.choice(chars) for _ in range(50)))"
  ```

  **Alternative methods:**
  - If you have Django installed in your backend:
    ```bash
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```
  - Online generator: https://djecrety.ir/

  **Example output:**
  ```
  NsXGImqZJKDxxlh%4KFASjMlHMycR@-xobMtLb&=zx7IJcI34e
  ```

  ⚠️ **NEVER commit this key to git!** Railway stores it securely as an environment variable.

- **${{service.VARIABLE}}**: This syntax tells Railway to reference another service's variable
  - Railway will automatically substitute the correct values
  - This enables secure service-to-service communication

4. **Set Custom Start Command**:
   - Still in Settings tab
   - Scroll to "Deploy"
   - Custom Start Command:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
   ```

5. **Configure Health Check**:
   - In Settings tab
   - Scroll to "Health Check"
   - Check Path: `/admin/`
   - Timeout: 100 seconds

### Step 4.3: Deploy Backend

1. **Generate Domain First**:
   - Go to "Settings" tab
   - Scroll to "Networking"
   - Under "Public Networking"
   - Click "Generate Domain"
   - Railway will give you a domain like: `backend-production-xyz.up.railway.app`
   - **Copy this URL** - you'll need it for frontend

2. **Start Deployment**:
   - Click "Deployments" tab
   - Click "Deploy" or Railway may auto-deploy
   - Watch the build logs in real-time

3. **Wait for Deployment** (3-5 minutes):
   - You'll see build logs streaming
   - Look for: "Installing dependencies..."
   - Then: "Collecting static files..."
   - Finally: "Deployment successful"

4. **Check Deployment Status**:
   - Green checkmark = Success ✅
   - Red X = Failed ❌ (check logs)

**✅ Checkpoint**: Backend should be deployed and running. The service card should show "Active" status.

---

## Part 5: Deploy Celery Worker

The Celery worker handles background tasks (CSV uploads, analytics calculations).

### Step 5.1: Create Celery Service

1. **Click "+ New"**
2. **Select "GitHub Repo"**
3. **Select the same repository**:
   - `DefoxxAnalytics/Refactoring_vstx-analytics-dashboard-v2`
4. **Cancel the auto-deployment** (we need to configure first)

### Step 5.2: Configure Celery Worker

1. **Rename Service**: `celery-worker`

2. **Set Build Configuration**:
   - Go to Settings → Build
   - Custom Dockerfile Path: `backend/Dockerfile.railway`
   - (Same Docker image as backend)

3. **Configure Environment Variables**:
   - Click "Variables" tab
   - Click "Add All Variables from" → Select `backend`
   - This copies all backend variables
   - **Remove these variables** (Celery doesn't need them):
     - `ALLOWED_HOSTS`
     - `CORS_ALLOWED_ORIGINS`
     - `CSRF_TRUSTED_ORIGINS`
     - `SECURE_SSL_REDIRECT`
     - `SESSION_COOKIE_SECURE`
     - `CSRF_COOKIE_SECURE`

4. **Set Custom Start Command**:
   - Settings → Deploy
   - Custom Start Command:
   ```bash
   celery -A config worker -l info --concurrency=2
   ```

5. **Disable Public Networking**:
   - Settings → Networking
   - Celery doesn't need public access
   - If a domain was generated, you can delete it
   - Click "Remove Public Domain"

### Step 5.3: Deploy Celery Worker

1. **Start Deployment**:
   - Go to Deployments tab
   - Click "Deploy"

2. **Monitor Logs**:
   - Watch for Celery startup messages
   - Look for: "celery@[hostname] ready"
   - Should show: "Connected to redis://..."

**✅ Checkpoint**: Celery worker should be running. Check logs for "ready" message.

---

## Part 6: Deploy Frontend Service

### Step 6.1: Create Frontend Service

1. **Click "+ New"**
2. **Select "GitHub Repo"**
3. **Select your repository**
4. **Cancel auto-deployment**

### Step 6.2: Configure Frontend Service

1. **Rename Service**: `frontend`

2. **Set Build Configuration**:
   - Settings → Build
   - Custom Dockerfile Path: `frontend/Dockerfile.railway`

3. **Set Build Arguments**:
   - These are needed during the Docker build
   - Settings → Build → Build Arguments
   - Add these **as Build Args, NOT environment variables**:

```bash
VITE_API_URL=https://[your-backend-domain]/api
VITE_APP_TITLE=Analytics Dashboard
VITE_APP_LOGO=/vtx_logo2.png
```

**Replace `[your-backend-domain]`** with the backend domain you generated in Step 4.3:
- Example: `https://backend-production-xyz.up.railway.app/api`
- ⚠️ Must include `/api` at the end
- ⚠️ Must use `https://` (not `http://`)

### Step 6.3: Deploy Frontend

1. **Generate Public Domain**:
   - Settings → Networking
   - Click "Generate Domain"
   - Copy this domain: `frontend-production-abc.up.railway.app`
   - **This is your application URL** 🎉

2. **Start Deployment**:
   - Go to Deployments tab
   - Click "Deploy"

3. **Wait for Build** (2-4 minutes):
   - Frontend build takes longer (compiling React)
   - Watch logs for: "Building Vite app..."
   - Then: "Copying to nginx..."
   - Finally: "Deployment successful"

**✅ Checkpoint**: All services deployed! You should see 5 service cards:
- `analytics-db` (PostgreSQL)
- `analytics-redis` (Redis)
- `backend` (Django)
- `celery-worker` (Celery)
- `frontend` (React + Nginx)

---

## Part 7: Initialize Database

Now we need to run Django migrations to create database tables.

### Step 7.1: Using Railway CLI (Recommended)

**If you installed the CLI:**

1. **Link to your project**:
   ```bash
   railway link
   ```
   - Select your project: `analytics-dashboard-production`

2. **Run migrations**:
   ```bash
   railway run -s backend python manage.py migrate
   ```
   - `-s backend` means "run this in the backend service"
   - Wait for migrations to complete (~30 seconds)

3. **Collect static files**:
   ```bash
   railway run -s backend python manage.py collectstatic --noinput
   ```

### Step 7.2: Using Railway Dashboard (Alternative)

**If you don't have CLI installed:**

1. **Open Backend Service**:
   - Click on `backend` card
   - Go to "Deployments" tab
   - Click on the active deployment (green checkmark)

2. **Open Shell**:
   - Look for "View Logs" dropdown
   - Click it and select "Open Shell" or "Run Command"

3. **Run Migration Command**:
   ```bash
   python manage.py migrate
   ```
   - Press Enter and wait
   - You'll see each migration being applied

4. **Run Collectstatic**:
   ```bash
   python manage.py collectstatic --noinput
   ```

**✅ Checkpoint**: Database tables created. You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying authentication.0001_initial... OK
  Applying procurement.0001_initial... OK
```

---

## Part 8: Create Admin User

### Step 8.1: Create Superuser

**Using Railway CLI:**

```bash
railway run -s backend python manage.py createsuperuser
```

**Or using Dashboard Shell:**

```bash
python manage.py createsuperuser
```

**Follow the prompts:**
```
Username: admin
Email: admin@versatexmsp.com
Password: [enter-secure-password]
Password (again): [confirm-password]
```

### Step 8.2: Create Organization and User Profile

The app requires users to have an organization and profile.

**Using Railway CLI:**

```bash
railway run -s backend python manage.py shell
```

**Or Dashboard Shell:**

```bash
python manage.py shell
```

**Then paste this code:**

```python
from apps.authentication.models import Organization, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

# Create default organization
org, created = Organization.objects.get_or_create(
    slug='default',
    defaults={'name': 'Default Organization'}
)
print(f"Organization: {org.name} (created: {created})")

# Get admin user (replace 'admin' with your username)
admin = User.objects.get(username='admin')

# Create or update profile
profile, created = UserProfile.objects.get_or_create(
    user=admin,
    defaults={
        'organization': org,
        'role': 'admin',
        'is_active': True
    }
)

if not created:
    profile.organization = org
    profile.role = 'admin'
    profile.is_active = True
    profile.save()

print(f"Profile created: {created}")
print(f"User: {admin.username}")
print(f"Role: {profile.role}")
print(f"Organization: {profile.organization.name}")
print("✅ Setup complete!")

# Exit shell
exit()
```

**Expected output:**
```
Organization: Default Organization (created: True)
Profile created: True
User: admin
Role: admin
Organization: Default Organization
✅ Setup complete!
```

**✅ Checkpoint**: Admin user created with proper organization and profile.

---

## Part 9: Test Your Deployment

### Step 9.1: Update Backend CORS Settings

Before testing, update backend to accept requests from frontend:

1. **Go to backend service** → Variables tab
2. **Update these variables**:

```bash
# Replace with your actual frontend domain
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.railway.app
CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.railway.app

# Update allowed hosts to include frontend domain
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},.railway.app,your-frontend-domain.railway.app
```

3. **Click "Save Changes"**
4. **Redeploy backend**:
   - Go to Deployments tab
   - Latest deployment will automatically restart

### Step 9.2: Test Frontend Access

1. **Open your frontend URL**: `https://your-frontend-domain.railway.app`

2. **You should see**:
   - Login page with Versatex logo
   - "Analytics Dashboard" title
   - Email and password fields

3. **If you see errors**:
   - Check browser console (F12)
   - Common issues:
     - "Failed to fetch" = CORS not configured
     - Blank page = API URL wrong in build args
     - 404 errors = Nginx routing issue

### Step 9.3: Test Login

1. **Enter your credentials**:
   - Email/Username: `admin`
   - Password: [your-password]

2. **Click "Sign In"**

3. **You should see**:
   - Dashboard with stat cards (may show $0 - that's ok, no data yet)
   - Sidebar with navigation
   - "Admin Panel" link with Shield icon (admin only)
   - User display in header showing your name and "Admin" badge

4. **If login fails**:
   - Check backend logs for errors
   - Verify user profile was created (Step 8.2)
   - Check CORS settings

### Step 9.4: Test Django Admin Panel

1. **Open backend URL**: `https://your-backend-domain.railway.app/admin/`

2. **You should see**:
   - Custom branded login with navy blue theme
   - Versatex logo
   - "Analytics Dashboard Admin Panel Login"

3. **Login with superuser credentials**

4. **You should see**:
   - Django admin dashboard
   - Navy blue header
   - "Analytics Dashboard Admin Panel" title
   - Links to: Users, Organizations, Suppliers, Categories, etc.

### Step 9.5: Test Admin Panel Link in Frontend

1. **Go back to frontend dashboard**
2. **Click "Admin Panel" in sidebar** (Shield icon)
3. **Should open Django admin in new tab**
4. **You should already be logged in** (JWT auth)

### Step 9.6: Test API Endpoints

1. **Open API docs**: `https://your-backend-domain.railway.app/api/docs`

2. **You should see**:
   - Swagger UI with all API endpoints
   - Authentication, Procurement, Analytics sections

3. **Test an endpoint**:
   - Click on `/api/analytics/overview/`
   - Click "Try it out"
   - Click "Execute"
   - Should return: `{"status": "success", "data": {...}}`

**✅ Checkpoint**: All tests passing! Your application is live and working! 🎉

---

## Part 10: Custom Domain Setup (Optional)

### Step 10.1: Add Custom Domain to Frontend

1. **Go to frontend service** → Settings → Networking

2. **Click "Add Custom Domain"**

3. **Enter your domain**:
   - Example: `analytics.yourdomain.com`
   - Or root: `yourdomain.com`

4. **Railway will show DNS instructions**:
   ```
   Type: CNAME
   Name: analytics (or @)
   Value: your-frontend-domain.railway.app
   TTL: 3600
   ```

5. **Add this CNAME record to your DNS provider**:
   - Go to your domain registrar (Namecheap, GoDaddy, Cloudflare, etc.)
   - Add the CNAME record exactly as shown
   - Wait for DNS propagation (5-60 minutes)

6. **Railway will auto-provision SSL certificate**:
   - This happens automatically
   - Wait for green checkmark
   - Your site will be accessible via HTTPS

### Step 10.2: Add Custom Domain to Backend

1. **Go to backend service** → Settings → Networking

2. **Add domain**: `api.yourdomain.com`

3. **Add CNAME record**:
   ```
   Type: CNAME
   Name: api
   Value: your-backend-domain.railway.app
   ```

### Step 10.3: Update Environment Variables

After custom domains are active:

**Backend variables:**
```bash
ALLOWED_HOSTS=api.yourdomain.com,${{RAILWAY_PUBLIC_DOMAIN}},.railway.app
CORS_ALLOWED_ORIGINS=https://analytics.yourdomain.com,https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://analytics.yourdomain.com,https://yourdomain.com
```

**Frontend rebuild required:**
- You need to rebuild frontend with new API URL
- Update Build Args: `VITE_API_URL=https://api.yourdomain.com/api`
- Trigger redeploy

---

## Part 11: Enable Auto-Deploy

Set up automatic deployments when you push to GitHub.

### Step 11.1: Configure Auto-Deploy for Each Service

**For Backend:**

1. **Go to backend service** → Settings
2. **Scroll to "Deploy"**
3. **Check "Automatic Deploys"**
4. **Source**: GitHub
5. **Branch**: `master` (or `main`)
6. **Root Directory**: (leave blank)

**Repeat for Celery Worker and Frontend**

### Step 11.2: Test Auto-Deploy

1. **Make a small change locally**:
   ```bash
   echo "# Railway auto-deploy test" >> README.md
   git add README.md
   git commit -m "Test Railway auto-deploy"
   git push origin master
   ```

2. **Watch Railway Dashboard**:
   - All 3 services should start deploying
   - Check deployment logs
   - Should complete in 3-5 minutes

**✅ Checkpoint**: Auto-deploy working! Future pushes will automatically deploy.

---

## Troubleshooting Common Issues

### Issue 1: Backend Won't Start

**Symptoms**: Backend deployment fails, logs show errors

**Common Causes & Solutions**:

1. **Missing Environment Variable**:
   ```
   Error: SECRET_KEY not set
   ```
   - Go to backend → Variables
   - Add missing variable
   - Redeploy

2. **Database Connection Failed**:
   ```
   Error: could not connect to server
   ```
   - Check `DATABASE_URL` is referencing correct service: `${{analytics-db.DATABASE_URL}}`
   - Ensure PostgreSQL service is running
   - Check database service logs

3. **Port Binding Error**:
   ```
   Error: Address already in use
   ```
   - Make sure start command uses `$PORT`: `--bind 0.0.0.0:$PORT`
   - Railway automatically sets PORT variable

### Issue 2: Frontend Shows Blank Page

**Symptoms**: Frontend loads but shows white screen

**Common Causes & Solutions**:

1. **Wrong API URL**:
   - Check browser console (F12)
   - Look for: `Failed to fetch` or `net::ERR_CONNECTION_REFUSED`
   - Fix: Update frontend Build Args with correct backend domain
   - Must rebuild frontend after changing build args

2. **CORS Error**:
   ```
   Access to fetch at 'https://backend...' has been blocked by CORS policy
   ```
   - Update backend `CORS_ALLOWED_ORIGINS` to include frontend domain
   - Update backend `CSRF_TRUSTED_ORIGINS` to include frontend domain
   - Redeploy backend

3. **Build Failed**:
   - Check frontend deployment logs
   - Look for: `Failed to compile` or `Module not found`
   - Usually means build args are missing

### Issue 3: Cannot Login

**Symptoms**: Login form submits but shows error

**Common Causes & Solutions**:

1. **403 Forbidden**:
   - CSRF token issue
   - Fix: Add frontend domain to `CSRF_TRUSTED_ORIGINS` on backend
   - Must include `https://`

2. **500 Internal Server Error**:
   - User profile missing
   - Re-run Step 8.2 to create profile
   - Check backend logs for actual error

3. **401 Unauthorized**:
   - Wrong credentials
   - Password doesn't match
   - Try creating new superuser

### Issue 4: Celery Tasks Not Running

**Symptoms**: CSV uploads fail, analytics don't update

**Common Causes & Solutions**:

1. **Celery Not Connected to Redis**:
   - Check celery-worker logs
   - Should see: "Connected to redis://..."
   - Fix: Verify `CELERY_BROKER_URL=${{analytics-redis.REDIS_URL}}`

2. **Celery Not Running**:
   - Check if celery-worker service is active
   - Look for "ready" message in logs
   - If crashed, check logs for Python errors

3. **Wrong Start Command**:
   - Ensure command is: `celery -A config worker -l info --concurrency=2`
   - Must use `config` (Django project name)

### Issue 5: Static Files Not Loading

**Symptoms**: Admin panel has no CSS, looks broken

**Common Causes & Solutions**:

1. **Collectstatic Not Run**:
   ```bash
   railway run -s backend python manage.py collectstatic --noinput
   ```

2. **WhiteNoise Not Configured**:
   - Should already be configured in `settings.py`
   - Check: `MIDDLEWARE` includes `WhiteNoiseMiddleware`

### Issue 6: Database Migrations Fail

**Symptoms**: Can't create tables, migration errors

**Common Solutions**:

1. **Reset Migrations** (if in development):
   ```bash
   # DON'T do this in production with real data!
   railway run -s backend python manage.py migrate --fake-initial
   ```

2. **Check Migration Files**:
   - Ensure all migration files are committed to git
   - Check backend logs for specific migration error

### Issue 7: Out of Memory (OOM)

**Symptoms**: Services crash with "Out of memory" error

**Solutions**:

1. **Upgrade Service Resources**:
   - Click service → Settings → Resources
   - Increase memory limit
   - Backend: upgrade to 1GB or 2GB
   - Cost will increase proportionally

2. **Reduce Workers**:
   - Backend: reduce from 4 to 2 workers in start command
   - Celery: reduce concurrency from 4 to 2

### Issue 8: High Costs

**Symptoms**: Railway bill higher than expected

**Solutions**:

1. **Check Usage**:
   - Go to Account → Usage
   - See which service uses most resources

2. **Optimize**:
   - Reduce backend workers
   - Reduce celery concurrency
   - Use smaller database tier for development

3. **Set Budget Limit**:
   - Account → Billing → Set Budget Alert
   - Get notified when approaching limit

### Issue 9: Slow Performance

**Symptoms**: App loads slowly, timeouts

**Solutions**:

1. **Check Service Health**:
   - Look at Railway metrics
   - High CPU or memory usage?

2. **Optimize Database**:
   - Add indexes to frequently queried fields
   - Upgrade database tier

3. **Enable Caching**:
   - Redis is already configured
   - Implement Django caching in views

4. **Use CDN** (for frontend):
   - Railway includes CDN automatically
   - Ensure static assets are cached

### Getting Help

**If you're still stuck:**

1. **Check Railway Status**: https://status.railway.app
2. **Railway Discord**: https://discord.gg/railway (very responsive!)
3. **Railway Docs**: https://docs.railway.app
4. **Check Service Logs**: Most issues are visible in logs

**When asking for help:**
- Share relevant logs (with sensitive data removed)
- Describe what you've tried
- Share your service configuration (screenshots)

---

## Success Checklist

Use this checklist to verify everything is working:

- [ ] Railway account created and payment method added
- [ ] GitHub repo connected to Railway
- [ ] PostgreSQL database created and running
- [ ] Redis cache created and running
- [ ] Backend service deployed with public domain
- [ ] Celery worker deployed and connected to Redis
- [ ] Frontend deployed with public domain
- [ ] Database migrations completed successfully
- [ ] Superuser created
- [ ] Organization and user profile created
- [ ] Frontend loads and shows login page with Versatex logo
- [ ] Can login successfully
- [ ] Dashboard displays (even if empty)
- [ ] Admin Panel link visible in sidebar (for admin)
- [ ] Django admin accessible and shows navy blue theme
- [ ] API documentation accessible
- [ ] User display shows in header with name and role badge
- [ ] Auto-deploy enabled for all services
- [ ] CORS configured correctly
- [ ] HTTPS working on all services
- [ ] Custom domain configured (if applicable)

---

## Next Steps After Deployment

1. **Load Sample Data**:
   - Upload a CSV file to test analytics
   - Go to Data Management → Upload CSV

2. **Create Additional Users**:
   - Django Admin → Users → Add User
   - Assign organization and role

3. **Configure Email** (for password resets):
   - Add SMTP settings to backend environment variables
   - See `.env.production.example` for email variables

4. **Set Up Monitoring**:
   - Consider adding Sentry for error tracking
   - Set up uptime monitoring (UptimeRobot, Pingdom)

5. **Backup Strategy**:
   - Railway auto-backs up PostgreSQL
   - Consider exporting data periodically
   - Document recovery procedures

6. **Performance Testing**:
   - Test with realistic data volumes
   - Monitor response times
   - Optimize queries if needed

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check Railway usage and costs
- Review error logs
- Test critical functionality

**Monthly**:
- Update dependencies (security patches)
- Review and optimize database
- Check backup integrity

**Quarterly**:
- Security audit
- Performance optimization
- Cost analysis

### Updating Your Application

**To deploy updates:**

1. **Make changes locally**
2. **Test thoroughly in development**
3. **Commit and push to GitHub**:
   ```bash
   git add .
   git commit -m "Your update description"
   git push origin master
   ```
4. **Railway auto-deploys** (if configured)
5. **Monitor deployment in Railway dashboard**
6. **Test production after deployment**

---

## Conclusion

Congratulations! You now have a production-ready Analytics Dashboard running on Railway! 🎉

**What you've accomplished:**
- ✅ Deployed a full-stack application with 5 services
- ✅ Configured PostgreSQL database and Redis cache
- ✅ Set up Django backend with Celery workers
- ✅ Deployed React frontend with custom branding
- ✅ Configured secure HTTPS access
- ✅ Set up automatic deployments from GitHub

**Your live application URLs:**
- Frontend: `https://your-frontend-domain.railway.app`
- Backend API: `https://your-backend-domain.railway.app/api`
- Django Admin: `https://your-backend-domain.railway.app/admin`
- API Docs: `https://your-backend-domain.railway.app/api/docs`

**Support:**
- Deployment Guide: This document
- Railway Guide: [docs/deployment/RAILWAY.md](RAILWAY.md)
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

**Happy deploying! 🚀**
