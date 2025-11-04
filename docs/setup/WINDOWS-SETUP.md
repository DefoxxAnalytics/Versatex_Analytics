# 🪟 Windows Setup Guide - Analytics Dashboard

## Quick Setup for Windows Users

This guide helps you set up the Analytics Dashboard on Windows without symlink issues.

---

## 📦 Package Information

**File:** `analytics-dashboard-fullstack-WINDOWS.zip` (1.3 MB)  
**Format:** Standard ZIP (Windows-compatible)  
**Node Modules:** Excluded (you'll install them locally)

---

## ✅ Prerequisites

Before starting, ensure you have:

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Version: 4.0 or higher
   - Enable WSL 2 backend (recommended)

2. **Git for Windows** (optional, for version control)
   - Download: https://git-scm.com/download/win

3. **Node.js** (if you want to run frontend locally)
   - Download: https://nodejs.org/ (LTS version)
   - Version: 18.x or higher

---

## 🚀 Step-by-Step Setup

### Step 1: Extract the Package

1. **Right-click** on `analytics-dashboard-fullstack-WINDOWS.zip`
2. Select **"Extract All..."**
3. Choose a destination folder (e.g., `C:\Projects\`)
4. Click **"Extract"**

**Result:** You should have a folder `analytics-dashboard-fullstack` with all files.

---

### Step 2: Configure Environment

1. **Open the extracted folder** in File Explorer
2. **Find the file** `.env.example`
3. **Copy it** and rename to `.env`
4. **Edit `.env`** with Notepad or your preferred text editor

**Minimum required settings:**
```env
# Database
DB_NAME=analytics_db
DB_USER=analytics_user
DB_PASSWORD=your_secure_password_here

# Django
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False

# Email (optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Generate a SECRET_KEY:**
- Visit: https://djecrety.ir/
- Copy the generated key
- Paste it in your `.env` file

---

### Step 3: Start Docker Services

1. **Open PowerShell** or **Command Prompt**
2. **Navigate to the project folder:**
   ```powershell
   cd C:\Projects\analytics-dashboard-fullstack
   ```

3. **Start Docker Compose:**
   ```powershell
   docker-compose up -d
   ```

4. **Wait for services to start** (about 1-2 minutes)

**Expected output:**
```
Creating analytics-db ... done
Creating analytics-redis ... done
Creating analytics-backend ... done
Creating analytics-celery ... done
Creating analytics-frontend ... done
```

---

### Step 4: Initialize Database

1. **Run migrations:**
   ```powershell
   docker-compose exec backend python manage.py migrate
   ```

2. **Create superuser:**
   ```powershell
   docker-compose exec backend python manage.py createsuperuser
   ```
   
   Enter your desired:
   - Username
   - Email
   - Password

---

### Step 5: Access the Application

Open your web browser and navigate to:

- **Frontend:** http://localhost
- **Django Admin:** http://localhost/api/admin
- **API Documentation:** http://localhost/api/docs

**Login with the superuser credentials you created in Step 4.**

---

## 🔧 Optional: Local Frontend Development

If you want to develop the frontend locally (not required for Docker deployment):

### Install Frontend Dependencies

1. **Open PowerShell** in the project folder
2. **Navigate to frontend:**
   ```powershell
   cd frontend
   ```

3. **Install pnpm** (if not already installed):
   ```powershell
   npm install -g pnpm
   ```

4. **Install dependencies:**
   ```powershell
   pnpm install
   ```

5. **Run development server:**
   ```powershell
   pnpm run dev
   ```

**Frontend will be available at:** http://localhost:5173

---

## 🛠️ Common Windows Issues & Solutions

### Issue 1: Docker Desktop Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
1. Start Docker Desktop from the Start Menu
2. Wait for Docker to fully start (whale icon in system tray)
3. Try the command again

---

### Issue 2: Port Already in Use

**Error:** `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution:**
1. Stop any web servers (IIS, Apache, nginx)
2. Or change the port in `docker-compose.yml`:
   ```yaml
   frontend:
     ports:
       - "8080:80"  # Use port 8080 instead
   ```
3. Access at http://localhost:8080

---

### Issue 3: Permission Denied

**Error:** `Permission denied` when running Docker commands

**Solution:**
1. Run PowerShell **as Administrator**
2. Or add your user to the `docker-users` group:
   - Open Computer Management
   - Go to Local Users and Groups → Groups
   - Double-click `docker-users`
   - Add your username
   - Restart your computer

---

### Issue 4: WSL 2 Not Enabled

**Error:** `WSL 2 installation is incomplete`

**Solution:**
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart your computer
4. Open Docker Desktop settings
5. Enable "Use the WSL 2 based engine"

---

## 📊 Verify Installation

### Check Docker Services

```powershell
docker-compose ps
```

**Expected output:**
```
Name                   State    Ports
analytics-backend      Up       0.0.0.0:8000->8000/tcp
analytics-db           Up       0.0.0.0:5432->5432/tcp
analytics-redis        Up       0.0.0.0:6379->6379/tcp
analytics-celery       Up
analytics-frontend     Up       0.0.0.0:80->80/tcp
```

All services should show **"Up"** status.

---

### Check Backend Logs

```powershell
docker-compose logs backend
```

Look for: `Listening at: http://0.0.0.0:8000`

---

### Check Frontend

Open http://localhost in your browser. You should see the login page.

---

## 🎯 Next Steps

1. **Login** with your superuser credentials
2. **Upload sample data** (CSV file with procurement data)
3. **Explore analytics pages:**
   - Overview
   - Suppliers
   - Categories
   - Pareto Analysis
   - Spend Stratification
   - Seasonality
   - Year-over-Year
   - Tail Spend

---

## 📚 Additional Resources

### Documentation Files

- `README.md` - Complete documentation
- `FINAL-DELIVERY.md` - Feature overview
- `TESTING-CHECKLIST.md` - Testing guide
- `TESTING-VERIFICATION.md` - Test results

### Docker Commands

**Stop all services:**
```powershell
docker-compose down
```

**Restart services:**
```powershell
docker-compose restart
```

**View logs:**
```powershell
docker-compose logs -f
```

**Remove all data (reset):**
```powershell
docker-compose down -v
```

---

## 🆘 Getting Help

### Check Logs

If something isn't working:

1. **Backend logs:**
   ```powershell
   docker-compose logs backend
   ```

2. **Frontend logs:**
   ```powershell
   docker-compose logs frontend
   ```

3. **Database logs:**
   ```powershell
   docker-compose logs db
   ```

### Common Log Messages

**"Waiting for database..."**
- Normal during startup
- Wait 30 seconds and try again

**"No migrations to apply"**
- Good! Database is up to date

**"Superuser created successfully"**
- Good! You can now login

---

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Project extracted from ZIP
- [ ] `.env` file created and configured
- [ ] `docker-compose up -d` successful
- [ ] Database migrations completed
- [ ] Superuser created
- [ ] Frontend accessible at http://localhost
- [ ] Login successful
- [ ] Sample data uploaded
- [ ] Analytics pages working

---

## 🎉 Congratulations!

Your Analytics Dashboard is now running on Windows!

**Key URLs:**
- Frontend: http://localhost
- Django Admin: http://localhost/api/admin
- API Docs: http://localhost/api/docs

**Happy analyzing!** 📊✨

---

## 💡 Pro Tips

1. **Use WSL 2** for better Docker performance on Windows
2. **Allocate more memory** to Docker (Settings → Resources)
3. **Use PowerShell 7** for better command-line experience
4. **Enable Hyper-V** for optimal Docker performance
5. **Keep Docker Desktop updated** for latest features

---

**Need more help?** Check the included documentation files or Docker logs for detailed information.
