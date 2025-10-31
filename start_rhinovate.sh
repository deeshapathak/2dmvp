#!/bin/bash

# Rhinovate AI - Complete Startup Script

echo "🎯 Starting Rhinovate AI - 2D MVP"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm and try again."
    exit 1
fi

print_success "All prerequisites found!"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Python dependencies installed!"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    print_success "Node.js dependencies installed!"
else
    print_error "Failed to install Node.js dependencies"
    exit 1
fi

cd ..

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend/uploads
print_success "Directories created!"

# Start backend in background
print_status "Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend started successfully (PID: $BACKEND_PID)"
else
    print_error "Failed to start backend"
    exit 1
fi

# Start frontend
print_status "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

print_success "Frontend started successfully (PID: $FRONTEND_PID)"

echo ""
echo "🎉 Rhinovate AI is now running!"
echo "=================================="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    print_status "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    print_success "Servers stopped!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
