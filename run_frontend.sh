#!/bin/bash

# Rhinovate AI Frontend Startup Script

echo "🎨 Starting Rhinovate AI Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd frontend
npm install

# Start the frontend
echo "🎯 Starting React development server on http://localhost:3000"
npm start
