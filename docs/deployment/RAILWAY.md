# Railway Deployment Guide

Complete guide for deploying the Analytics Dashboard to Railway.

> **🚀 NEW: Looking for a detailed step-by-step walkthrough?**
> Check out [RAILWAY-STEP-BY-STEP.md](RAILWAY-STEP-BY-STEP.md) for a comprehensive beginner-friendly guide with detailed screenshots descriptions and troubleshooting!

## Quick Links

- **[Step-by-Step Guide](RAILWAY-STEP-BY-STEP.md)** - Detailed walkthrough (RECOMMENDED for first-time deployment)
- **[This Guide](#deployment-steps)** - Quick reference for experienced users
- **[Troubleshooting](#troubleshooting)** - Common issues and solutions

## Why Railway?

Railway is the recommended platform for this application because:

- **Perfect Stack Match**: Native support for Django + Celery + Redis + PostgreSQL
- **Cost-Effective**: $30-50/month for production deployment
- **Easy Setup**: Deploy in under 15 minutes
- **No Cold Starts**: Services run 24/7
- **Built-in CI/CD**: Auto-deploy from GitHub
- **Zero-Config Networking**: Services communicate securely

## Cost Estimate

### Development/Staging
- Backend: $10-15/month
- Celery Worker: $5-10/month
- PostgreSQL: $5/month
- Redis: $3-5/month
- Frontend: $5/month
- **Total: ~$30-40/month**

### Production (Medium Traffic)
- Backend: $15-20/month
- Celery Worker: $10/month
- PostgreSQL: $10-15/month
- Redis: $5-8/month
- Frontend: $5-10/month
- **Total: ~$45-65/month**

> Railway uses usage-based pricing, so you only pay for what you use.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code must be in a GitHub repo
3. **Railway CLI** (optional but recommended):
   ```bash
   npm install -g @railway/cli
   ```

## Deployment Steps

### Step 1: Prepare Your Repository

Ensure these files are committed:
- ✅ `railway.toml` - Railway configuration
- ✅ `.env.production.example` - Production environment template
- ✅ `backend/Dockerfile` - Backend Docker configuration
- ✅ `frontend/Dockerfile` - Frontend Docker configuration
- ✅ `docker-compose.yml` - Service definitions

### Step 2: Create Railway Project

#### Option A: Using Railway Dashboard (Recommended)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your repository**: `DefoxxAnalytics/Refactoring_vstx-analytics-dashboard-v2`
5. **Railway will detect your services** from docker-compose.yml

#### Option B: Using Railway CLI

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Link to your GitHub repo
railway link
```

### Step 3: Add Database Services

1. **Add PostgreSQL Database**:
   - Click "+ New" in your project
   - Select "Database" → "Add PostgreSQL"
   - Railway automatically creates `DATABASE_URL` variable
   - Name it: `analytics-db`

2. **Add Redis**:
   - Click "+ New" in your project
   - Select "Database" → "Add Redis"
   - Railway automatically creates `REDIS_URL` variable
   - Name it: `analytics-redis`

### Step 4: Configure Backend Service

1. **Create Backend Service**:
   - Click "+ New" → "GitHub Repo"
   - Select your repository
   - Name: `backend`
   - Root Directory: Leave empty (Railway will detect)
   - Dockerfile Path: `backend/Dockerfile`

2. **Set Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=config.settings
   SECRET_KEY=<generate-new-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},.railway.app
   DATABASE_URL=${{analytics-db.DATABASE_URL}}
   REDIS_URL=${{analytics-redis.REDIS_URL}}
   CELERY_BROKER_URL=${{analytics-redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{analytics-redis.REDIS_URL}}
   CORS_ALLOWED_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
   CSRF_TRUSTED_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   TZ=America/New_York
   PYTHONUNBUFFERED=1
   ```

   **Generate SECRET_KEY:**
   ```bash
   # Works without Django installed
   python -c "import secrets, string; chars = string.ascii_letters + string.digits + '@#$%^&*()_+-='; print(''.join(secrets.choice(chars) for _ in range(50)))"
   ```
   Or use: https://djecrety.ir/

3. **Set Custom Start Command** (in Settings → Deploy):
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

4. **Configure Health Check** (in Settings → Health Check):
   - Path: `/admin/`
   - Timeout: 100 seconds

5. **Generate Public Domain**:
   - Go to Settings → Networking
   - Click "Generate Domain"
   - Save this URL (e.g., `backend-production.up.railway.app`)

### Step 5: Configure Celery Worker Service

1. **Create Celery Service**:
   - Click "+ New" → "GitHub Repo"
   - Select same repository
   - Name: `celery-worker`
   - Dockerfile Path: `backend/Dockerfile`

2. **Set Environment Variables** (same as backend):
   ```
   DJANGO_SETTINGS_MODULE=config.settings
   SECRET_KEY=<same-as-backend>
   DATABASE_URL=${{analytics-db.DATABASE_URL}}
   REDIS_URL=${{analytics-redis.REDIS_URL}}
   CELERY_BROKER_URL=${{analytics-redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{analytics-redis.REDIS_URL}}
   TZ=America/New_York
   PYTHONUNBUFFERED=1
   ```

3. **Set Custom Start Command**:
   ```bash
   celery -A config worker -l info --concurrency=2
   ```

4. **Disable Public URL** (in Settings → Networking):
   - Celery worker doesn't need public access
   - Remove/disable the public domain

### Step 6: Configure Frontend Service

1. **Create Frontend Service**:
   - Click "+ New" → "GitHub Repo"
   - Select same repository
   - Name: `frontend`
   - Dockerfile Path: `frontend/Dockerfile`

2. **Set Build Arguments** (in Settings → Build):
   ```
   VITE_API_URL=https://<your-backend-domain>/api
   VITE_APP_TITLE=Analytics Dashboard
   VITE_APP_LOGO=/vtx_logo2.png
   ```

3. **Generate Public Domain**:
   - Go to Settings → Networking
   - Click "Generate Domain"
   - This is your main application URL

### Step 7: Run Database Migrations

Once backend is deployed:

```bash
# Using Railway CLI
railway run -s backend python manage.py migrate

# Or use Railway dashboard shell
# Select backend service → Shell tab → Run:
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 8: Create Superuser

```bash
# Using Railway CLI
railway run -s backend python manage.py createsuperuser

# Or use Railway dashboard shell
# Follow prompts to create admin user
```

### Step 9: Create Initial Organization

```bash
# Using Railway CLI
railway run -s backend python manage.py shell

# Then in shell:
from apps.authentication.models import Organization, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()
org = Organization.objects.create(name="Default Organization", slug="default")

# Link admin user to organization
admin = User.objects.get(username="admin")  # or your superuser username
profile, created = UserProfile.objects.get_or_create(
    user=admin,
    defaults={
        'organization': org,
        'role': 'admin',
        'is_active': True
    }
)
print(f"Profile created: {created}")
```

### Step 10: Update CORS Settings

After both services are deployed, update backend environment variables:

```bash
# In backend service settings, update these with actual domains:
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
CSRF_TRUSTED_ORIGINS=https://your-frontend.railway.app
ALLOWED_HOSTS=your-backend.railway.app,.railway.app
```

Click "Redeploy" after updating.

## Verify Deployment

1. **Test Frontend**: Visit your frontend URL
   - Should see login page with Versatex logo

2. **Test Backend API**: Visit `https://your-backend.railway.app/api/docs`
   - Should see API documentation

3. **Test Django Admin**: Visit `https://your-backend.railway.app/admin/`
   - Should see custom branded admin panel
   - Login with superuser credentials

4. **Test Login**: Login through frontend
   - Should successfully authenticate
   - Admin users should see "Admin Panel" link with Shield icon

## Custom Domain Setup (Optional)

### Backend Domain

1. Go to backend service → Settings → Networking
2. Click "Add Custom Domain"
3. Enter your domain: `api.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   CNAME api.yourdomain.com → your-backend.railway.app
   ```
5. Railway automatically provisions SSL certificate

### Frontend Domain

1. Go to frontend service → Settings → Networking
2. Click "Add Custom Domain"
3. Enter your domain: `yourdomain.com` or `app.yourdomain.com`
4. Add CNAME record:
   ```
   CNAME yourdomain.com → your-frontend.railway.app
   ```

### Update Environment Variables

After adding custom domains:

```bash
# Backend service
ALLOWED_HOSTS=api.yourdomain.com,your-backend.railway.app,.railway.app
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Frontend service (build args)
VITE_API_URL=https://api.yourdomain.com/api
```

Redeploy both services after updating.

## CI/CD Setup

Railway automatically deploys when you push to GitHub:

1. **Enable Auto-Deploy**:
   - Go to each service → Settings → Deploy
   - Enable "Automatic Deployments"
   - Select branch: `main` or `master`

2. **Deploy Triggers**:
   - Push to branch → Auto-deploy
   - Pull request merged → Auto-deploy
   - Manual trigger from dashboard

3. **Deployment Notifications**:
   - Enable webhooks in Settings → Webhooks
   - Integrate with Slack/Discord for notifications

## Monitoring and Logs

### View Logs

```bash
# Using CLI
railway logs -s backend
railway logs -s celery-worker
railway logs -s frontend

# Or use dashboard
# Select service → Logs tab
```

### Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response times

Access: Select service → Metrics tab

### Alerts (Optional)

Set up alerts for:
- High CPU usage (>80%)
- High memory usage (>90%)
- Service crashes
- Database connection issues

## Scaling

### Vertical Scaling (Increase Resources)

1. Go to service → Settings → Resources
2. Adjust:
   - CPU allocation
   - Memory limit
   - Disk size (for databases)

### Horizontal Scaling (Multiple Instances)

```bash
# In service settings
Instances: 1 → 2 (or more)
```

Railway automatically load-balances between instances.

**Note**: Ensure your app is stateless for horizontal scaling. Session data should be in Redis or database.

## Backup Strategy

### Database Backups

Railway automatically backs up PostgreSQL:
- Automated daily backups
- 7-day retention (Starter plan)
- 30-day retention (Pro plan)

**Manual Backup**:
```bash
# Using Railway CLI
railway run -s analytics-db pg_dump > backup.sql

# Restore
railway run -s analytics-db psql < backup.sql
```

### Media Files Backup

If using local storage, set up periodic backups:
```bash
# Add volume to backend service
# Use Railway volumes or S3 for persistent storage
```

## Troubleshooting

### Issue: Backend won't start

**Check**:
1. Environment variables are set correctly
2. DATABASE_URL is properly formatted
3. Migrations are up to date
4. Check logs: `railway logs -s backend`

**Solution**:
```bash
railway run -s backend python manage.py migrate
railway restart -s backend
```

### Issue: CORS errors in frontend

**Check**:
1. CORS_ALLOWED_ORIGINS includes frontend domain
2. CSRF_TRUSTED_ORIGINS includes frontend domain
3. Both use `https://` (not `http://`)

**Solution**:
Update backend env vars and redeploy.

### Issue: Celery tasks not running

**Check**:
1. Celery worker is running (check logs)
2. Redis connection is working
3. CELERY_BROKER_URL is correct

**Solution**:
```bash
railway logs -s celery-worker
railway restart -s celery-worker
```

### Issue: Static files not loading

**Check**:
1. `collectstatic` was run
2. WhiteNoise is configured (already in settings.py)
3. STATIC_ROOT is set correctly

**Solution**:
```bash
railway run -s backend python manage.py collectstatic --noinput
railway restart -s backend
```

### Issue: Database connection errors

**Check**:
1. PostgreSQL service is running
2. DATABASE_URL is correct
3. Database has sufficient resources

**Solution**:
```bash
# Check PostgreSQL status
railway status -s analytics-db

# Restart if needed
railway restart -s analytics-db
```

## Cost Optimization Tips

1. **Right-size your services**: Start small, scale up as needed
2. **Use shared CPU**: More cost-effective for low-traffic apps
3. **Optimize Docker images**: Smaller images = faster deployments = lower costs
4. **Enable auto-sleep** for non-production environments
5. **Monitor usage**: Check Railway metrics to identify waste
6. **Use caching**: Leverage Redis to reduce database queries
7. **Optimize Celery**: Adjust worker concurrency based on load

## Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (generate new one, don't use .env.example)
- ✅ `SECURE_SSL_REDIRECT=True`
- ✅ `SESSION_COOKIE_SECURE=True`
- ✅ `CSRF_COOKIE_SECURE=True`
- ✅ `ALLOWED_HOSTS` configured properly
- ✅ Database passwords are strong
- ✅ Environment variables are not committed to git
- ✅ Use Railway secrets for sensitive data
- ✅ Enable 2FA on Railway account
- ✅ Restrict database access to Railway network only

## Rollback

If deployment fails:

```bash
# Using CLI - rollback to previous deployment
railway rollback -s backend

# Or use dashboard
# Service → Deployments → Click previous deployment → "Redeploy"
```

## Migration from Local to Railway

1. **Export local data**:
   ```bash
   docker-compose exec backend python manage.py dumpdata > data.json
   ```

2. **Import to Railway**:
   ```bash
   railway run -s backend python manage.py loaddata data.json
   ```

3. **Copy media files** (if any):
   ```bash
   # Upload to S3 or Railway volumes
   ```

## Support and Resources

- **Railway Documentation**: https://docs.railway.app
- **Railway Community**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app
- **Django on Railway Guide**: https://docs.railway.app/guides/django

## Next Steps

After successful deployment:

1. ✅ Set up custom domains
2. ✅ Configure email service (for password resets)
3. ✅ Set up error tracking (Sentry)
4. ✅ Configure monitoring (Railway metrics + external)
5. ✅ Set up automated backups
6. ✅ Document your deployment process
7. ✅ Train team on Railway dashboard

## Estimated Timeline

- **Initial Setup**: 15-20 minutes
- **Database Migration**: 5 minutes
- **Testing**: 10 minutes
- **Custom Domain Setup**: 15 minutes (if needed)
- **Total**: ~1 hour for complete production deployment

---

**Deployed successfully?** Update your team documentation and celebrate! 🎉
