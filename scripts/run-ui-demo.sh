#!/bin/bash

# FinRisk AI Copilot - UI Demo Script
# This script sets up and runs the frontend UI for demonstration

set -e

echo "🚀 Starting FinRisk AI Copilot UI Demo"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18 or higher is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) is installed"
}

# Check if npm is installed
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    print_success "npm $(npm --version) is installed"
}

# Navigate to the frontend directory
navigate_to_frontend() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    FRONTEND_DIR="$PROJECT_ROOT/apps/gateway-bff"
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    print_success "Changed to frontend directory: $FRONTEND_DIR"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in current directory"
        exit 1
    fi
    
    if [ ! -d "node_modules" ]; then
        print_status "node_modules not found, running npm install..."
        npm install
    else
        print_status "Dependencies already installed, checking for updates..."
        npm ci
    fi
    
    print_success "Dependencies installed successfully"
}

# Create environment file if it doesn't exist
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env.local" ]; then
        print_status "Creating .env.local file..."
        cat > .env.local << EOF
# Application Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:3000/api/graphql
NODE_ENV=development

# Backend Service URLs (mock for demo)
CASE_SERVICE_URL=http://localhost:8081
INGESTION_SERVICE_URL=http://localhost:8082
ML_SCORING_SERVICE_URL=http://localhost:8083
SEARCH_SERVICE_URL=http://localhost:8084
COPILOT_SERVICE_URL=http://localhost:8085
RULES_SERVICE_URL=http://localhost:8086
ENTITY_SERVICE_URL=http://localhost:8087

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_REAL_TIME_UPDATES=true
ENABLE_ADVANCED_ANALYTICS=true
EOF
        print_success "Environment file created"
    else
        print_success "Environment file already exists"
    fi
}

# Build the application
build_application() {
    print_status "Building the application..."
    
    npm run build
    
    print_success "Application built successfully"
}

# Start the development server
start_dev_server() {
    print_status "Starting development server..."
    
    echo ""
    echo "🎉 FinRisk AI Copilot UI is starting..."
    echo ""
    echo "📱 Access the application at: http://localhost:3000"
    echo "🔍 GraphQL Playground: http://localhost:3000/api/graphql"
    echo ""
    echo "✨ Features available in this demo:"
    echo "   • Dashboard with real-time metrics"
    echo "   • Case management interface"
    echo "   • AI-powered insights and chat"
    echo "   • Advanced search capabilities"
    echo "   • Risk analytics and reporting"
    echo "   • Interactive data visualizations"
    echo ""
    echo "🛠  Demo Data:"
    echo "   • Mock cases and entities"
    echo "   • Simulated real-time alerts"
    echo "   • Sample AI insights"
    echo "   • Example risk metrics"
    echo ""
    echo "⚡ Quick Actions:"
    echo "   • Press Ctrl+C to stop the server"
    echo "   • Open http://localhost:3000 in your browser"
    echo "   • Use ⌘+K for quick search"
    echo ""
    
    # Start the server
    npm run dev
}

# Main execution
main() {
    echo ""
    print_status "Checking prerequisites..."
    check_node
    check_npm
    
    print_status "Setting up the application..."
    navigate_to_frontend
    setup_environment
    install_dependencies
    
    print_status "Starting the demo..."
    start_dev_server
}

# Handle interruption
cleanup() {
    echo ""
    print_warning "Demo stopped by user"
    echo ""
    echo "Thank you for trying FinRisk AI Copilot! 🙏"
    echo ""
    echo "To run the demo again:"
    echo "  ./scripts/run-ui-demo.sh"
    echo ""
    echo "For more information, see:"
    echo "  • README.md - Project documentation"
    echo "  • docs/ARCHITECTURE.md - System architecture"
    echo "  • apps/gateway-bff/README.md - Frontend documentation"
    echo ""
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
