# Deployment Guide

This guide covers deploying the CDRP API to various cloud platforms. Choose the option that best fits your needs:

## Quick Deployment Options

### 1. Railway (Recommended - Easiest)
Railway offers the simplest deployment with automatic database provisioning.

#### Steps:
1. **Sign up at [railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Deploy with one click:**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Initial deployment"
   git push origin main
   
   # Then deploy on Railway:
   # 1. Go to railway.app
   # 2. Click "Deploy from GitHub"
   # 3. Select your repository
   # 4. Railway will automatically detect the railway.toml file
   ```

4. **Set environment variables in Railway dashboard:**
   ```
   FLASK_ENV=production
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
   SECRET_KEY=your-super-secret-key-change-this
   ```

5. **Add PostgreSQL database:**
   - In Railway dashboard, click "Add Service" → "Database" → "PostgreSQL"
   - Railway will automatically set the DATABASE_URL environment variable

6. **Your API will be live at:** `https://your-app-name.railway.app`

### 2. Render (Free Tier Available)
Render provides excellent free hosting with automatic SSL.

#### Steps:
1. **Sign up at [render.com](https://render.com)**
2. **Connect your GitHub repository**
3. **Create a new Web Service:**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`

4. **Add PostgreSQL database:**
   - Create a new PostgreSQL service in Render
   - Copy the connection string

5. **Set environment variables:**
   ```
   FLASK_ENV=production
   DATABASE_URL=<your-postgres-connection-string>
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
   SECRET_KEY=your-super-secret-key-change-this
   ```

6. **Deploy:** Render will automatically deploy when you push to GitHub

### 3. Heroku (Popular Choice)
Heroku is a mature platform with excellent documentation.

#### Steps:
1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Other platforms: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-cdrp-api-name
   ```

3. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
   heroku config:set SECRET_KEY=your-super-secret-key-change-this
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Run database migrations:**
   ```bash
   heroku run flask db upgrade
   heroku run python scripts/seed_data.py
   ```

### 4. Docker + Cloud Run / AWS / DigitalOcean

#### Build and test locally:
```bash
# Build the Docker image
docker build -t cdrp-api .

# Run with Docker Compose (includes PostgreSQL and Redis)
docker-compose up -d

# Your API will be available at http://localhost:5000
```

#### Deploy to Google Cloud Run:
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cdrp-api

# Deploy to Cloud Run
gcloud run deploy cdrp-api \
  --image gcr.io/YOUR_PROJECT_ID/cdrp-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables Reference

Set these environment variables in your deployment platform:

### Required
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
SECRET_KEY=your-super-secret-key-minimum-32-characters
```

### Optional
```bash
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
CORS_ORIGINS=https://your-frontend-domain.com,https://your-app.com
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Post-Deployment Steps

### 1. Initialize Database
Most platforms will run the release command automatically, but you can also run manually:

```bash
# For Heroku
heroku run flask db upgrade
heroku run python scripts/seed_data.py

# For Railway/Render (usually automatic)
# Check the deployment logs

# For Docker
docker exec -it container_name flask db upgrade
docker exec -it container_name python scripts/seed_data.py
```

### 2. Test Your Deployment

```bash
# Replace YOUR_DOMAIN with your actual domain
export API_URL="https://your-app-name.railway.app"

# Test health check
curl $API_URL/health

# Test login
curl -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test with token (replace TOKEN with actual token from login)
curl -H "Authorization: Bearer TOKEN" \
  $API_URL/api/regions
```

### 3. Security Checklist

- [ ] Changed all default passwords
- [ ] Set strong JWT_SECRET_KEY and SECRET_KEY
- [ ] Configured CORS_ORIGINS for your frontend domains
- [ ] Enabled HTTPS (should be automatic on most platforms)
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting with Redis (optional)

## Troubleshooting

### Common Issues

1. **"Application Error" on startup:**
   - Check environment variables are set correctly
   - Verify DATABASE_URL is valid
   - Check deployment logs for specific errors

2. **Database connection errors:**
   - Ensure DATABASE_URL is correctly formatted
   - For Heroku: Make sure it starts with `postgresql://` not `postgres://`
   - Check if database addon is properly attached

3. **JWT/Authentication errors:**
   - Verify JWT_SECRET_KEY is set and at least 32 characters
   - Ensure SECRET_KEY is set

4. **CORS errors:**
   - Set CORS_ORIGINS to include your frontend domain
   - For development, you can use `*` but this is not recommended for production

### Platform-Specific Debugging

#### Railway
```bash
# View logs
railway logs

# Connect to shell
railway shell
```

#### Render
- Check the deployment logs in the Render dashboard
- Use the "Shell" feature to run commands

#### Heroku
```bash
# View logs
heroku logs --tail

# Run commands
heroku run bash
```

## Performance Optimization

### For Production
1. **Use Redis for rate limiting:**
   ```bash
   # Add Redis addon (platform-dependent)
   # Set REDIS_URL environment variable
   ```

2. **Configure worker processes:**
   ```bash
   # In Procfile or start command
   gunicorn app:app --workers 4 --timeout 120
   ```

3. **Enable database connection pooling:**
   - Most cloud databases include this automatically
   - For custom setups, configure in your DATABASE_URL

4. **Set up monitoring:**
   - Use platform-native monitoring
   - Consider services like Sentry for error tracking

## Custom Domain (Optional)

### Railway
1. Go to Settings → Domains
2. Add your custom domain
3. Update your DNS records as instructed

### Render
1. Go to Settings → Custom Domains
2. Add your domain and configure DNS

### Heroku
```bash
heroku domains:add your-domain.com
# Follow instructions to configure DNS
```

## Backup Strategy

### Database Backups
- **Railway/Render:** Automatic backups included
- **Heroku:** Use `heroku pg:backups:capture`
- **Docker:** Set up pg_dump cron jobs

### Code Backups
- Keep your code in GitHub/GitLab
- Tag releases for easy rollbacks
- Use platform-specific rollback features when needed

Your CDRP API should now be running live on the internet! 🚀

Choose the platform that best fits your needs:
- **Railway:** Easiest setup, great for getting started
- **Render:** Good free tier, reliable
- **Heroku:** Most features, well-documented
- **Docker:** Maximum control, can deploy anywhere