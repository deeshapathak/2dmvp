#!/bin/bash

# Rhinovate AI Backend Startup Script

echo "🚀 Starting Rhinovate AI Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create uploads directory
mkdir -p backend/uploads

# Start the backend
echo "🎯 Starting FastAPI server on http://localhost:8000"
cd backend
python3 main.py
