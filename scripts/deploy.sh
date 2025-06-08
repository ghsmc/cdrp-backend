#!/bin/bash

# CDRP API Deployment Script
# This script helps with common deployment tasks

set -e  # Exit on any error

echo "🚀 CDRP API Deployment Helper"
echo "================================"

# Function to generate a secure secret key
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

# Function to check if required tools are installed
check_dependencies() {
    echo "📋 Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git is required but not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 is required but not installed"
        exit 1
    fi
    
    echo "✅ Dependencies check passed"
}

# Function to prepare for deployment
prepare_deployment() {
    echo "📦 Preparing for deployment..."
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        echo "🔄 Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit for CDRP API"
    else
        echo "🔄 Adding changes to git..."
        git add .
        if git diff --staged --quiet; then
            echo "ℹ️  No changes to commit"
        else
            git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
        fi
    fi
    
    echo "✅ Deployment preparation complete"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    echo ""
    echo "1. Go to https://railway.app"
    echo "2. Sign up/Login with GitHub"
    echo "3. Click 'Deploy from GitHub'"
    echo "4. Select this repository"
    echo "5. Add these environment variables:"
    echo "   FLASK_ENV=production"
    echo "   JWT_SECRET_KEY=$(generate_secret)"
    echo "   SECRET_KEY=$(generate_secret)"
    echo "6. Add PostgreSQL database service"
    echo ""
    echo "🔗 Your API will be live at: https://your-project-name.railway.app"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    echo ""
    echo "1. Go to https://render.com"
    echo "2. Sign up/Login with GitHub"
    echo "3. Create new Web Service from GitHub repo"
    echo "4. Use these settings:"
    echo "   - Runtime: Python 3"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT --workers 2"
    echo "5. Add PostgreSQL database"
    echo "6. Set environment variables:"
    echo "   FLASK_ENV=production"
    echo "   JWT_SECRET_KEY=$(generate_secret)"
    echo "   SECRET_KEY=$(generate_secret)"
    echo "   DATABASE_URL=<from your PostgreSQL service>"
    echo ""
    echo "🔗 Your API will be live at: https://your-service-name.onrender.com"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🔮 Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Install it first:"
        echo "   brew tap heroku/brew && brew install heroku"
        exit 1
    fi
    
    echo "Please enter your Heroku app name (or press Enter for auto-generated):"
    read -r app_name
    
    if [ -z "$app_name" ]; then
        heroku create
    else
        heroku create "$app_name"
    fi
    
    echo "🔧 Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:mini
    
    echo "🔧 Setting environment variables..."
    heroku config:set FLASK_ENV=production
    heroku config:set JWT_SECRET_KEY="$(generate_secret)"
    heroku config:set SECRET_KEY="$(generate_secret)"
    
    echo "🚀 Deploying to Heroku..."
    git push heroku main
    
    echo "🔧 Running database migrations..."
    heroku run flask db upgrade
    heroku run python scripts/seed_data.py
    
    echo "✅ Deployment complete!"
    heroku open
}

# Function to test deployment
test_deployment() {
    echo "🧪 Testing deployment..."
    
    echo "Enter your API URL (e.g., https://your-app.railway.app):"
    read -r api_url
    
    echo "Testing health check..."
    if curl -f "$api_url/health" > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        return 1
    fi
    
    echo "Testing login..."
    response=$(curl -s -X POST "$api_url/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    if echo "$response" | grep -q "access_token"; then
        echo "✅ Login test passed"
        echo "🎉 Your CDRP API is working correctly!"
        echo "🔗 API URL: $api_url"
        echo "👤 Admin login: admin / admin123"
        echo "📚 API docs: $api_url/docs (if enabled)"
    else
        echo "❌ Login test failed"
        echo "Response: $response"
        return 1
    fi
}

# Function to setup local Docker development
setup_docker() {
    echo "🐳 Setting up Docker development environment..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    echo "🔧 Starting services with Docker Compose..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "🔧 Running database migrations..."
    docker-compose exec web flask db upgrade
    
    echo "🌱 Seeding database..."
    docker-compose exec web python scripts/seed_data.py
    
    echo "✅ Docker environment ready!"
    echo "🔗 API URL: http://localhost:5000"
    echo "📊 Database: PostgreSQL on localhost:5432"
    echo "📨 Redis: localhost:6379"
}

# Main menu
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Railway (Recommended - Easiest)"
    echo "2) Render (Free tier available)"
    echo "3) Heroku (Full-featured)"
    echo "4) Docker (Local development)"
    echo "5) Test existing deployment"
    echo "6) Generate secret keys"
    echo "0) Exit"
    echo ""
    echo -n "Enter your choice [0-6]: "
}

# Generate secret keys
generate_keys() {
    echo "🔑 Generated secret keys:"
    echo "JWT_SECRET_KEY=$(generate_secret)"
    echo "SECRET_KEY=$(generate_secret)"
    echo ""
    echo "⚠️  Keep these keys secure and use them in your environment variables!"
}

# Main script
main() {
    check_dependencies
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                prepare_deployment
                deploy_railway
                ;;
            2)
                prepare_deployment
                deploy_render
                ;;
            3)
                prepare_deployment
                deploy_heroku
                ;;
            4)
                setup_docker
                ;;
            5)
                test_deployment
                ;;
            6)
                generate_keys
                ;;
            0)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please try again."
                ;;
        esac
        
        echo ""
        echo "Press Enter to continue..."
        read -r
    done
}

# Run main function
main "$@"