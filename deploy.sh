#!/bin/bash

# Railway Deployment Script for Australian Immigration Law RAG System
# Usage: ./deploy.sh

set -e

echo "🚀 Starting Railway Deployment for Australian Immigration Law RAG System"
echo "====================================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Australian Immigration Law RAG System"
    echo "✅ Git repository initialized"
else
    echo "📝 Git repository already exists"
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ No GitHub remote found!"
    echo "Please:"
    echo "1. Create a new repository on GitHub"
    echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "3. Run: git push -u origin main"
    echo "4. Then run this script again"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git add .
git commit -m "Update for Railway deployment" || echo "No changes to commit"
git push origin main
echo "✅ Code pushed to GitHub"

echo ""
echo "🎯 Next Steps:"
echo "1. Go to https://railway.app and create a new project"
echo "2. Connect your GitHub repository"
echo "3. Railway will auto-detect railway.json and deploy the backend"
echo "4. Add environment variables in Railway dashboard:"
echo "   - HF_TOKEN=your_huggingface_token"
echo "   - CORS_ORIGINS=*"
echo "5. Create a second service for the frontend using Dockerfile.frontend"
echo "6. Set VITE_API_URL in frontend service to your backend URL"
echo ""

echo "🎉 Deployment preparation complete!"
echo "Your app will be available at: https://your-project-name.up.railway.app"
