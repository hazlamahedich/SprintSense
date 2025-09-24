#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${GREEN}Starting development environment...${NC}"

# Check for required tools
check_requirements() {
    local missing_tools=()

    if ! command -v poetry &> /dev/null; then
        missing_tools+=("poetry")
    fi

    if ! command -v node &> /dev/null; then
        missing_tools+=("node")
    fi

    if ! command -v npm &> /dev/null; then
        missing_tools+=("npm")
    fi

    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required tools: ${missing_tools[*]}${NC}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
}

# Function to kill processes on a port
kill_port() {
    local port=$1
    if lsof -i ":$port" > /dev/null; then
        echo -e "${RED}Killing process on port $port${NC}"
        lsof -i ":$port" | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
    fi
}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    while ! nc -z localhost 5432; do
        sleep 1
    done
    echo -e "${GREEN}PostgreSQL is ready!${NC}"
}

# Function to ensure PostgreSQL is running
ensure_postgres() {
    if ! docker ps | grep -q "postgres:16.2"; then
        echo -e "${YELLOW}Starting PostgreSQL...${NC}"
        docker run --name sprintsense-postgres \
            -e POSTGRES_USER=sprintsense \
            -e POSTGRES_PASSWORD=sprintsense \
            -e POSTGRES_DB=sprintsense \
            -p 5432:5432 \
            -d postgres:16.2

        wait_for_postgres
    else
        echo -e "${GREEN}PostgreSQL is already running.${NC}"
    fi
}

# Install dependencies if needed
install_dependencies() {
    # Backend dependencies
    cd "$BACKEND_DIR" || exit
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}Installing backend dependencies...${NC}"
        poetry install
    fi
    cd "$PROJECT_ROOT"

    # Frontend dependencies
    cd "$FRONTEND_DIR" || exit
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    cd "$PROJECT_ROOT"
}

# Kill any existing processes
echo "Cleaning up existing processes..."
kill_port 3000
kill_port 5173  # Vite's default port
kill_port 8000

# Check requirements
check_requirements

# Ensure PostgreSQL is running
ensure_postgres

# Install dependencies if needed
install_dependencies

# Start backend server
echo -e "${GREEN}Starting backend server...${NC}"
cd "$BACKEND_DIR" || exit
poetry run alembic upgrade head  # Run database migrations
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend server
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$FRONTEND_DIR" || exit
npm run dev &
FRONTEND_PID=$!

# Function to handle script exit
cleanup() {
    echo -e "${YELLOW}Shutting down development environment...${NC}"

    # Kill running servers
    if [ ! -z "$BACKEND_PID" ] && ps -p $BACKEND_PID > /dev/null; then
        echo -e "${YELLOW}Stopping backend server...${NC}"
        kill $BACKEND_PID 2>/dev/null
    fi

    if [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${YELLOW}Stopping frontend server...${NC}"
        kill $FRONTEND_PID 2>/dev/null
    fi

    # Clean up ports
    kill_port 3000
    kill_port 5173
    kill_port 8000

    # Ask about stopping PostgreSQL
    read -p "Stop PostgreSQL container? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Stopping PostgreSQL...${NC}"
        docker stop sprintsense-postgres
        docker rm sprintsense-postgres
    fi

    echo -e "${GREEN}Development environment shutdown complete!${NC}"
    exit 0
}

# Register cleanup function
trap cleanup INT TERM

echo -e "${GREEN}Development environment is running!${NC}"
echo -e "${GREEN}Services:${NC}"
echo -e "  Backend API: ${NC}http://localhost:8000${NC}"
echo -e "  Frontend:    ${NC}http://localhost:5173${NC}"
echo -e "  API Docs:    ${NC}http://localhost:8000/docs${NC}"
echo -e "  Database:    ${NC}localhost:5432${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for processes to finish
wait
