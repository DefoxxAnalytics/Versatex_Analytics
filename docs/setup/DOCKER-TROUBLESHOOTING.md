# 🐳 Docker Troubleshooting Guide

## Common Docker Build & Runtime Issues

This guide helps you resolve common Docker issues when deploying the Analytics Dashboard.

---

## ✅ Issue Fixed: Frontend Dockerfile Path

**Error:**
```
ERROR [frontend stage-1 2/3] COPY --from=builder /app/dist/public /usr/share/nginx/html
"/app/dist/public": not found
```

**Status:** ✅ **FIXED** in this package

**What was wrong:**
- Dockerfile was looking for `/app/dist/public`
- Vite builds to `/app/dist` (not `/app/dist/public`)

**Fix applied:**
```dockerfile
# Before (incorrect)
COPY --from=builder /app/dist/public /usr/share/nginx/html

# After (correct)
COPY --from=builder /app/dist /usr/share/nginx/html
```

---

## 🚀 Quick Start Commands

### Start All Services
```bash
docker-compose up -d
```

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop All Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild Services
```bash
# Rebuild all
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build frontend
docker-compose up -d --build backend
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:**
```
Bind for 0.0.0.0:80 failed: port is already allocated
```

**Solution 1: Change Port**

Edit `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "8080:80"  # Use port 8080 instead of 80
```

Then access at: http://localhost:8080

**Solution 2: Stop Conflicting Service**

Windows:
```powershell
# Check what's using port 80
netstat -ano | findstr :80

# Stop IIS if running
iisreset /stop
```

Linux/Mac:
```bash
# Check what's using port 80
sudo lsof -i :80

# Stop the service
sudo systemctl stop apache2  # or nginx
```

---

### Issue 2: Database Connection Failed

**Error:**
```
django.db.utils.OperationalError: could not connect to server: Connection refused
```

**Solution:**

1. **Check database is running:**
   ```bash
   docker-compose ps db
   ```

2. **Wait for database to be ready:**
   ```bash
   # Database takes 10-30 seconds to start
   docker-compose logs db
   ```

3. **Verify environment variables:**
   ```bash
   # Check .env file
   cat .env | grep DB_
   ```

4. **Restart services in order:**
   ```bash
   docker-compose down
   docker-compose up -d db
   # Wait 30 seconds
   docker-compose up -d backend
   docker-compose up -d frontend
   ```

---

### Issue 3: Frontend Shows 502 Bad Gateway

**Error:**
Browser shows "502 Bad Gateway" when accessing http://localhost

**Solution:**

1. **Check backend is running:**
   ```bash
   docker-compose ps backend
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

3. **Verify backend health:**
   ```bash
   curl http://localhost:8000/api/
   ```

4. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

---

### Issue 4: Frontend Build Failed

**Error:**
```
ERROR [frontend builder 6/6] RUN pnpm exec vite build
```

**Solution:**

1. **Check if pnpm-lock.yaml exists:**
   ```bash
   ls -la frontend/pnpm-lock.yaml
   ```

2. **Rebuild with no cache:**
   ```bash
   docker-compose build --no-cache frontend
   docker-compose up -d frontend
   ```

3. **Check Node.js version:**
   ```dockerfile
   # In frontend/Dockerfile
   FROM node:22-alpine AS builder  # Should be Node 18+
   ```

---

### Issue 5: Backend Migrations Failed

**Error:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**

1. **Reset database (development only):**
   ```bash
   docker-compose down -v  # Removes volumes
   docker-compose up -d db
   # Wait 30 seconds
   docker-compose up -d backend
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

2. **Or manually reset:**
   ```bash
   docker-compose exec db psql -U analytics_user -d analytics_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
   docker-compose exec backend python manage.py migrate
   ```

---

### Issue 6: Permission Denied (Linux/Mac)

**Error:**
```
Permission denied while trying to connect to the Docker daemon socket
```

**Solution:**

1. **Add user to docker group:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Or use sudo:**
   ```bash
   sudo docker-compose up -d
   ```

---

### Issue 7: Out of Disk Space

**Error:**
```
no space left on device
```

**Solution:**

1. **Clean up Docker:**
   ```bash
   # Remove unused containers
   docker container prune -f
   
   # Remove unused images
   docker image prune -a -f
   
   # Remove unused volumes
   docker volume prune -f
   
   # Remove everything unused
   docker system prune -a --volumes -f
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

---

### Issue 8: Slow Build on Windows

**Issue:**
Docker builds are extremely slow on Windows

**Solution:**

1. **Enable WSL 2 backend:**
   - Open Docker Desktop
   - Settings → General
   - Enable "Use the WSL 2 based engine"
   - Restart Docker Desktop

2. **Move project to WSL 2:**
   ```powershell
   # In WSL 2 terminal
   cd ~
   unzip /mnt/c/Downloads/analytics-dashboard-fullstack-WINDOWS.zip
   cd analytics-dashboard-fullstack
   docker-compose up -d
   ```

3. **Allocate more resources:**
   - Docker Desktop → Settings → Resources
   - Increase CPU and Memory
   - Apply & Restart

---

### Issue 9: Environment Variables Not Working

**Error:**
Settings in `.env` file are not being used

**Solution:**

1. **Verify .env file location:**
   ```bash
   # Must be in project root
   ls -la .env
   ```

2. **Check .env syntax:**
   ```bash
   # No spaces around =
   DB_NAME=analytics_db        # ✅ Correct
   DB_NAME = analytics_db      # ❌ Wrong
   ```

3. **Restart services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Verify variables are loaded:**
   ```bash
   docker-compose exec backend env | grep DB_
   ```

---

### Issue 10: CORS Errors in Browser

**Error:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**

1. **Check CORS settings in backend:**
   ```python
   # backend/config/settings.py
   CORS_ALLOWED_ORIGINS = [
       "http://localhost",
       "http://localhost:80",
       "http://localhost:8080",
   ]
   ```

2. **Add your domain:**
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost",
       "https://yourdomain.com",
   ]
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

---

## 🔧 Advanced Troubleshooting

### View Container Details

```bash
# Inspect container
docker inspect analytics-backend

# Check container logs
docker logs analytics-backend

# Execute command in container
docker exec -it analytics-backend sh

# Check container resource usage
docker stats
```

### Network Issues

```bash
# List networks
docker network ls

# Inspect network
docker network inspect analytics-dashboard-fullstack_default

# Test connectivity between containers
docker exec analytics-backend ping db
docker exec analytics-backend ping redis
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U analytics_user -d analytics_db

# List tables
\dt

# Check data
SELECT COUNT(*) FROM procurement_transaction;

# Exit
\q
```

### Redis Access

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check keys
KEYS *

# Exit
exit
```

---

## 📊 Health Check Commands

### Check All Services

```bash
#!/bin/bash
echo "=== Docker Services ==="
docker-compose ps

echo -e "\n=== Database Health ==="
docker-compose exec db pg_isready -U analytics_user

echo -e "\n=== Redis Health ==="
docker-compose exec redis redis-cli ping

echo -e "\n=== Backend Health ==="
curl -s http://localhost:8000/api/ | head -5

echo -e "\n=== Frontend Health ==="
curl -s http://localhost/health
```

Save as `check-health.sh` and run:
```bash
chmod +x check-health.sh
./check-health.sh
```

---

## 🚨 Emergency Reset

If everything is broken and you want to start fresh:

```bash
# Stop all services
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a --volumes -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Initialize database
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

**⚠️ Warning:** This will delete all data!

---

## 📝 Logging Best Practices

### Enable Debug Logging

Edit `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

Restart services:
```bash
docker-compose restart backend
```

### Save Logs to File

```bash
# All logs
docker-compose logs > logs.txt

# Specific service
docker-compose logs backend > backend-logs.txt

# Follow logs and save
docker-compose logs -f backend | tee backend-logs.txt
```

---

## ✅ Verification Checklist

After fixing issues, verify everything works:

- [ ] All services show "Up" status: `docker-compose ps`
- [ ] Database is healthy: `docker-compose exec db pg_isready`
- [ ] Redis is healthy: `docker-compose exec redis redis-cli ping`
- [ ] Backend API responds: `curl http://localhost:8000/api/`
- [ ] Frontend loads: Open http://localhost in browser
- [ ] Login works: Use superuser credentials
- [ ] Can upload CSV: Test data upload
- [ ] Analytics pages work: Check all 8 pages

---

## 🆘 Getting More Help

### Collect Diagnostic Information

```bash
# System info
docker version
docker-compose version

# Service status
docker-compose ps

# All logs
docker-compose logs > full-logs.txt

# Environment
cat .env

# Disk space
df -h
```

### Useful Resources

- Docker Documentation: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- PostgreSQL: https://www.postgresql.org/docs/

---

## 🎉 Success!

If all services are running and you can access the application, congratulations! Your Analytics Dashboard is ready to use.

**Next Steps:**
1. Upload sample procurement data
2. Explore analytics pages
3. Create additional users
4. Configure production settings

**Happy analyzing!** 📊✨
