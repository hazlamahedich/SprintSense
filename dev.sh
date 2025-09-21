#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${GREEN}Starting development environment...${NC}"

# Function to kill processes on a port
kill_port() {
    local port=$1
    if lsof -i ":$port" > /dev/null; then
        echo -e "${RED}Killing process on port $port${NC}"
        lsof -i ":$port" | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    fi
}

# Kill any existing processes
echo "Cleaning up existing processes..."
kill_port 3000
kill_port 5173  # Vite's default port
kill_port 8000

# Start backend server
echo -e "${GREEN}Starting backend server...${NC}"
cd "$BACKEND_DIR" || exit
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend server
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$FRONTEND_DIR" || exit
npm run dev &
FRONTEND_PID=$!

# Function to handle script exit
cleanup() {
    echo -e "${RED}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill_port 3000
    kill_port 5173
    kill_port 8000
    exit 0
}

# Register cleanup function
trap cleanup INT TERM

echo -e "${GREEN}Development environment is running!${NC}"
echo "Backend server: http://localhost:8000"
echo "Frontend server: http://localhost:5173"
echo -e "${GREEN}Press Ctrl+C to stop all servers${NC}"

# Wait for both processes
wait
