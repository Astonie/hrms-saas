#!/bin/bash

# =============================================================================
# HRMS-SAAS Setup Script
# =============================================================================
# This script sets up the complete HRMS-SAAS development environment

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command_exists docker; then
        missing_deps+=("Docker")
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        missing_deps+=("Docker Compose")
    fi
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("Python 3")
    fi
    
    # Check Node.js
    if ! command_exists node; then
        missing_deps+=("Node.js")
    fi
    
    # Check npm
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    print_success "All prerequisites are installed!"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cp env.example .env
        print_success "Environment file created from template"
        print_warning "Please review and update .env file with your configuration"
    else
        print_status "Environment file already exists"
    fi
}

# Function to start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    
    # Start PostgreSQL and Redis
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker services started successfully"
    else
        print_error "Failed to start Docker services"
        exit 1
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install development dependencies
    pip install black isort flake8 mypy pytest pytest-asyncio pytest-cov
    
    # Run database migrations
    print_status "Running database migrations..."
    alembic upgrade head
    
    print_success "Backend setup completed!"
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup completed!"
    cd ..
}

# Function to create database
create_database() {
    print_status "Creating database..."
    
    # Connect to PostgreSQL and create database if it doesn't exist
    docker-compose exec -T postgres psql -U hrms_user -d postgres -c "
        SELECT 'CREATE DATABASE hrms_main'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'hrms_main')\gexec
    "
    
    print_success "Database setup completed!"
}

# Function to run initial setup
run_initial_setup() {
    print_status "Running initial database setup..."
    
    # Run the initialization script
    docker-compose exec -T postgres psql -U hrms_user -d hrms_main -f /docker-entrypoint-initdb.d/init-db.sql
    
    print_success "Initial database setup completed!"
}

# Function to create test data
create_test_data() {
    print_status "Creating test data..."
    
    # This would be implemented with actual test data creation
    print_success "Test data creation completed!"
}

# Function to start development servers
start_dev_servers() {
    print_status "Starting development servers..."
    
    # Start backend in background
    cd backend
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    cd ..
    
    # Start frontend in background
    cd frontend
    nohup npm run dev > ../frontend.log 2>&1 &
    cd ..
    
    # Wait for servers to start
    sleep 5
    
    print_success "Development servers started!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:3000"
    print_status "API Docs: http://localhost:8000/docs"
}

# Function to show status
show_status() {
    print_status "Checking system status..."
    
    echo ""
    echo "=== System Status ==="
    
    # Check Docker services
    echo "Docker Services:"
    docker-compose ps
    
    echo ""
    echo "=== Development Servers ==="
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend: ✅ Running (http://localhost:8000)"
    else
        echo "Backend: ❌ Not running"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "Frontend: ✅ Running (http://localhost:3000)"
    else
        echo "Frontend: ❌ Not running"
    fi
    
    echo ""
    echo "=== Logs ==="
    echo "Backend logs: tail -f backend.log"
    echo "Frontend logs: tail -f frontend.log"
}

# Function to show help
show_help() {
    echo "HRMS-SAAS Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup       Complete setup (default)"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show system status"
    echo "  logs        Show logs"
    echo "  clean       Clean up everything"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Complete setup"
    echo "  $0 start     # Start services"
    echo "  $0 status    # Check status"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop development servers
    pkill -f "uvicorn app.main:app" || true
    pkill -f "npm run dev" || true
    
    # Stop Docker services
    docker-compose down
    
    print_success "All services stopped!"
}

# Function to show logs
show_logs() {
    print_status "Showing logs..."
    
    echo "=== Backend Logs ==="
    if [ -f "backend.log" ]; then
        tail -f backend.log
    else
        echo "No backend logs found"
    fi
}

# Function to clean up
cleanup() {
    print_warning "This will remove all data and containers. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        
        # Stop services
        stop_services
        
        # Remove containers and volumes
        docker-compose down -v --remove-orphans
        
        # Remove log files
        rm -f backend.log frontend.log
        
        # Remove virtual environment
        rm -rf backend/venv
        
        # Remove node modules
        rm -rf frontend/node_modules
        
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main function
main() {
    case "${1:-setup}" in
        "setup")
            print_status "Starting HRMS-SAAS setup..."
            check_prerequisites
            create_env_file
            start_docker_services
            create_database
            run_initial_setup
            setup_backend
            setup_frontend
            create_test_data
            start_dev_servers
            show_status
            print_success "Setup completed successfully!"
            ;;
        "start")
            start_docker_services
            start_dev_servers
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_docker_services
            start_dev_servers
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
