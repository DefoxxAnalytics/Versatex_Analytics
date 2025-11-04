# 🔧 Quick Fix: Database Migration Issue

## Error You're Seeing

```
django.db.utils.ProgrammingError: relation "authentication_userprofile" does not exist
```

## Root Cause

The database migrations weren't run before trying to create the superuser. The database tables don't exist yet.

---

## ✅ Solution: Run Migrations First

Follow these commands **in order**:

### Step 1: Check Services Are Running

```powershell
docker-compose ps
```

**Expected:** All services should show "Up" status.

---

### Step 2: Run Database Migrations

```powershell
docker-compose exec backend python manage.py migrate
```

**Expected output:**
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying authentication.0001_initial... OK
  Applying procurement.0001_initial... OK
  Applying analytics.0001_initial... OK
  ...
```

**This creates all the database tables.**

---

### Step 3: Now Create Superuser

```powershell
docker-compose exec backend python manage.py createsuperuser
```

**Follow the prompts:**
- Username: `admin` (or your choice)
- Email: your email
- Password: your password (min 8 characters)

**If password is too simple, type `y` to bypass validation.**

---

## 🎯 Complete Setup Sequence

Here's the correct order for first-time setup:

```powershell
# 1. Start Docker services
docker-compose up -d

# 2. Wait for services to be ready (30 seconds)
timeout /t 30

# 3. Check services are running
docker-compose ps

# 4. Run migrations (IMPORTANT - do this first!)
docker-compose exec backend python manage.py migrate

# 5. Create superuser (now this will work)
docker-compose exec backend python manage.py createsuperuser

# 6. Access the application
# Open browser: http://localhost
```

---

## 🔍 Verify Migrations Were Applied

Check if tables exist:

```powershell
docker-compose exec db psql -U analytics_user -d analytics_db -c "\dt"
```

**You should see tables like:**
- `auth_user`
- `authentication_userprofile`
- `authentication_organization`
- `procurement_transaction`
- `procurement_supplier`
- `procurement_category`
- etc.

---

## 🆘 If Migrations Fail

### Error: "No migrations to apply"

This is actually **good** - it means migrations already ran.

### Error: "Database connection refused"

**Solution:**
```powershell
# Wait for database to be ready
docker-compose logs db

# Look for: "database system is ready to accept connections"
# Then try migrations again
```

### Error: "Permission denied"

**Solution:**
```powershell
# Run PowerShell as Administrator
# Or check .env file has correct database credentials
```

---

## 🔄 Reset Database (If Needed)

If everything is broken and you want to start fresh:

```powershell
# Stop services and remove volumes
docker-compose down -v

# Start services again
docker-compose up -d

# Wait 30 seconds for database to initialize
timeout /t 30

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

**⚠️ Warning:** This deletes all data!

---

## ✅ Success Checklist

- [ ] Services running: `docker-compose ps` shows all "Up"
- [ ] Migrations applied: `docker-compose exec backend python manage.py migrate`
- [ ] Tables exist: `docker-compose exec db psql -U analytics_user -d analytics_db -c "\dt"`
- [ ] Superuser created: `docker-compose exec backend python manage.py createsuperuser`
- [ ] Can login: Open http://localhost and login with superuser credentials

---

## 📝 Common Mistakes

### ❌ Wrong Order
```powershell
# DON'T do this:
docker-compose up -d
docker-compose exec backend python manage.py createsuperuser  # ❌ Tables don't exist yet!
```

### ✅ Correct Order
```powershell
# DO this:
docker-compose up -d
docker-compose exec backend python manage.py migrate           # ✅ Create tables first
docker-compose exec backend python manage.py createsuperuser   # ✅ Now create user
```

---

## 🎉 After Successful Setup

Once migrations are applied and superuser is created:

1. **Open browser:** http://localhost
2. **Login** with your superuser credentials
3. **Upload sample data** (CSV file)
4. **Explore analytics pages**

---

## 💡 Pro Tips

### Check Migration Status

```powershell
# See which migrations are applied
docker-compose exec backend python manage.py showmigrations
```

### Create Sample Data

```powershell
# After superuser is created, you can create sample data
docker-compose exec backend python manage.py shell
```

Then in Python shell:
```python
from apps.procurement.models import Supplier, Category, Transaction
from apps.authentication.models import Organization
from django.contrib.auth.models import User

# Get your user and organization
user = User.objects.first()
org = user.profile.organization

# Create sample supplier
supplier = Supplier.objects.create(
    name="Acme Corp",
    organization=org
)

# Create sample category
category = Category.objects.create(
    name="Office Supplies",
    organization=org
)

# Create sample transaction
Transaction.objects.create(
    supplier=supplier,
    category=category,
    amount=1000.00,
    date="2024-01-15",
    organization=org
)

print("Sample data created!")
exit()
```

---

## 🔧 Useful Commands

### View Backend Logs
```powershell
docker-compose logs backend
```

### View Database Logs
```powershell
docker-compose logs db
```

### Restart Backend
```powershell
docker-compose restart backend
```

### Access Django Shell
```powershell
docker-compose exec backend python manage.py shell
```

### Access Database
```powershell
docker-compose exec db psql -U analytics_user -d analytics_db
```

---

## 📚 Related Documentation

- **WINDOWS-SETUP.md** - Complete Windows setup guide
- **DOCKER-TROUBLESHOOTING.md** - Docker issues and solutions
- **README.md** - Main documentation

---

## ✅ Quick Reference Card

**First Time Setup:**
```powershell
docker-compose up -d                                          # Start services
docker-compose exec backend python manage.py migrate         # Create tables
docker-compose exec backend python manage.py createsuperuser # Create admin
```

**Restart Services:**
```powershell
docker-compose restart
```

**View Logs:**
```powershell
docker-compose logs -f backend
```

**Reset Everything:**
```powershell
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## 🎉 You're Ready!

After following these steps, your Analytics Dashboard will be fully operational.

**Happy analyzing!** 📊✨
