# 🚀 Deploy CDRP API in 5 Minutes

## Option 1: Railway (Recommended - Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### Steps:
1. **Click the Railway button above** or go to [railway.app](https://railway.app)
2. **Sign up with GitHub** (free account)
3. **Deploy from GitHub:**
   - Click "Deploy from GitHub"
   - Select this repository
   - Railway auto-detects the configuration

4. **Add PostgreSQL database:**
   - In your project dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway automatically connects it to your app

5. **Set environment variables** (in Railway dashboard):
   ```
   FLASK_ENV=production
   JWT_SECRET_KEY=your-super-secret-32-char-key-here
   SECRET_KEY=your-another-secret-32-char-key
   ```

6. **Done!** Your API will be live at `https://your-project.railway.app`

---

## Option 2: Render (Free Tier)

### Steps:
1. **Go to [render.com](https://render.com)** and sign up with GitHub
2. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Runtime:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`

3. **Add PostgreSQL:**
   - Create new PostgreSQL service
   - Copy the connection string

4. **Set environment variables:**
   ```
   FLASK_ENV=production
   DATABASE_URL=<your-postgres-connection-string>
   JWT_SECRET_KEY=<generate-32-char-secret>
   SECRET_KEY=<generate-32-char-secret>
   ```

5. **Deploy!** Render automatically deploys on git push

---

## Option 3: Quick Local Docker

If you have Docker installed:

```bash
# Clone and run
git clone <your-repo>
cd "CDRP API"
docker-compose up -d

# Your API is now running at http://localhost:5000
```

---

## 🧪 Test Your Deployment

Replace `YOUR_API_URL` with your actual URL:

```bash
# Health check
curl https://YOUR_API_URL/health

# Login test
curl -X POST https://YOUR_API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 🔑 Default Credentials

After deployment, you can login with:
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ IMPORTANT: Change this password immediately in production!**

---

## 🔧 Environment Variables Generator

Run this to generate secure secret keys:

```bash
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

---

## 📚 What You Get

✅ **Complete REST API** with authentication  
✅ **Role-based permissions** (Admin, Coordinator, Field Agent, Viewer)  
✅ **Relief request management** with CRUD operations  
✅ **Search and filtering** capabilities  
✅ **Analytics dashboard** endpoints  
✅ **Audit logging** for all actions  
✅ **Rate limiting** and security features  
✅ **PostgreSQL database** with migrations  
✅ **Comprehensive documentation**  

---

## 🆘 Need Help?

1. **Check the logs** in your deployment platform
2. **Verify environment variables** are set correctly
3. **Ensure database is connected** and migrations ran
4. **Run the deployment script:** `./scripts/deploy.sh`
5. **Read the full guide:** `docs/DEPLOYMENT.md`

---

## 🎯 Quick API Examples

Once deployed, try these endpoints:

```bash
# Get regions
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://YOUR_API_URL/api/regions

# Create relief request
curl -X POST https://YOUR_API_URL/api/requests \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Emergency Relief Needed",
    "description": "Urgent assistance required...",
    "location": "City Center",
    "severity": "high",
    "disaster_type_id": 1,
    "region_id": 1
  }'
```

**Your disaster relief API is now live on the internet! 🌍**