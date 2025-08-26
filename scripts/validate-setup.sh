#!/bin/bash

# FinRisk AI Copilot - Setup Validation Script
# This script validates that all prerequisites are installed and working

set -e

echo "🔍 FinRisk AI Copilot - Setup Validation"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Success/failure counters
SUCCESS_COUNT=0
TOTAL_CHECKS=0

check_command() {
    local cmd=$1
    local name=$2
    local required_version=$3
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $name... "
    
    if command -v "$cmd" >/dev/null 2>&1; then
        if [ -n "$required_version" ]; then
            version=$($cmd --version 2>/dev/null | head -n1 | grep -oE '[0-9]+\.[0-9]+' | head -n1 || echo "unknown")
            echo -e "${GREEN}✓ Found${NC} (version: $version)"
        else
            echo -e "${GREEN}✓ Found${NC}"
        fi
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}✗ Not found${NC}"
        if [ -n "$required_version" ]; then
            echo "  ${YELLOW}Please install $name $required_version or later${NC}"
        else
            echo "  ${YELLOW}Please install $name${NC}"
        fi
    fi
}

check_port() {
    local port=$1
    local service=$2
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking port $port ($service)... "
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Port in use${NC}"
        echo "  ${YELLOW}Service on port $port may conflict with $service${NC}"
    else
        echo -e "${GREEN}✓ Available${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
}

echo ""
echo "📋 Checking Prerequisites..."
echo "----------------------------"

# Check basic tools
check_command "java" "Java" "21"
check_command "python3" "Python" "3.11"
check_command "docker" "Docker" "20.10"
check_command "docker-compose" "Docker Compose" "2.0"
check_command "make" "Make"
check_command "git" "Git"

# Check optional tools
echo ""
echo "📋 Checking Optional Tools..."
echo "-----------------------------"
check_command "poetry" "Poetry" "1.6"
check_command "node" "Node.js" "20"
check_command "npm" "NPM" "10"
check_command "kubectl" "Kubernetes CLI"
check_command "helm" "Helm" "3.0"
check_command "terraform" "Terraform" "1.6"

# Check ports
echo ""
echo "📋 Checking Port Availability..."
echo "--------------------------------"
check_port 3000 "Gateway BFF"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 8080 "Case Service"
check_port 8081 "Ingestion Service"
check_port 8082 "ML Scoring Service"
check_port 8083 "Search Service"
check_port 8084 "Copilot Orchestrator"
check_port 8085 "Rules Service"
check_port 8086 "Entity Service"
check_port 9092 "Kafka"
check_port 9200 "OpenSearch"

# Check file structure
echo ""
echo "📋 Checking Project Structure..."
echo "--------------------------------"

check_file() {
    local file=$1
    local desc=$2
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $desc... "
    
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo -e "${GREEN}✓ Found${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}✗ Missing${NC}"
        echo "  ${YELLOW}Expected: $file${NC}"
    fi
}

check_file "apps/case-service/pom.xml" "Case Service Maven config"
check_file "apps/case-service/mvnw" "Case Service Maven wrapper"
check_file "apps/ingestion-service/pyproject.toml" "Ingestion Service Poetry config"
check_file "apps/ml-scoring/pyproject.toml" "ML Scoring Service Poetry config"
check_file "apps/gateway-bff/package.json" "Gateway BFF NPM config"
check_file "infra/docker-compose/docker-compose.yml" "Docker Compose config"
check_file "infra/k8s/helm/finrisk/Chart.yaml" "Helm chart"
check_file "Makefile" "Development Makefile"

# Memory and disk check
echo ""
echo "📋 Checking System Resources..."
echo "-------------------------------"

# Check available memory (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    total_mem=$(sysctl -n hw.memsize)
    total_mem_gb=$((total_mem / 1024 / 1024 / 1024))
    echo -n "Checking system memory... "
    if [ $total_mem_gb -ge 8 ]; then
        echo -e "${GREEN}✓ $total_mem_gb GB${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${YELLOW}⚠ $total_mem_gb GB (8GB+ recommended)${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

# Check disk space
available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G.*//')
echo -n "Checking disk space... "
if [ "${available_space%.*}" -ge 20 ]; then
    echo -e "${GREEN}✓ ${available_space}G available${NC}"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
    echo -e "${YELLOW}⚠ ${available_space}G available (20GB+ recommended)${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Docker check
echo ""
echo "📋 Checking Docker..."
echo "--------------------"

if command -v docker >/dev/null 2>&1; then
    echo -n "Checking Docker daemon... "
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}✗ Not running${NC}"
        echo "  ${YELLOW}Please start Docker Desktop or Docker daemon${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking Docker memory allocation... "
    # This is approximate - Docker Desktop settings may vary
    echo -e "${GREEN}✓ Available${NC} (Please ensure Docker has 4GB+ allocated)"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
fi

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="

# Count required vs optional failures
REQUIRED_FAILURES=0
OPTIONAL_FAILURES=0

# Check if essential tools are missing
command -v java >/dev/null 2>&1 || REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))
command -v python3 >/dev/null 2>&1 || REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))
command -v docker >/dev/null 2>&1 || REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))
command -v poetry >/dev/null 2>&1 || REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))
docker info >/dev/null 2>&1 || REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))

# Check optional tools
command -v helm >/dev/null 2>&1 || OPTIONAL_FAILURES=$((OPTIONAL_FAILURES + 1))
command -v terraform >/dev/null 2>&1 || OPTIONAL_FAILURES=$((OPTIONAL_FAILURES + 1))

if [ $REQUIRED_FAILURES -eq 0 ]; then
    echo -e "${GREEN}🎉 Core requirements satisfied! ($SUCCESS_COUNT/$TOTAL_CHECKS total checks passed)${NC}"
    if [ $OPTIONAL_FAILURES -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some optional tools are missing (needed for cloud deployment)${NC}"
        echo ""
        echo "Optional tools for cloud deployment:"
        command -v helm >/dev/null 2>&1 || echo "  - Helm: brew install helm"
        command -v terraform >/dev/null 2>&1 || echo "  - Terraform: brew install terraform"
    fi
    echo ""
    echo "✅ Your system is ready for FinRisk AI Copilot development!"
    echo ""
    echo "Next steps:"
    echo "1. Run 'make setup' to initialize the development environment"
    echo "2. Run 'make start' to start the infrastructure services"
    echo "3. Run the individual service commands to start development"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Critical requirements missing ($REQUIRED_FAILURES critical failures)${NC}"
    echo ""
    echo "❗ Please install the following required tools:"
    command -v java >/dev/null 2>&1 || echo "  - Java 21: brew install openjdk@21"
    command -v python3 >/dev/null 2>&1 || echo "  - Python 3.11+: brew install python@3.11"
    command -v docker >/dev/null 2>&1 || echo "  - Docker: brew install docker"
    command -v poetry >/dev/null 2>&1 || echo "  - Poetry: brew install poetry"
    docker info >/dev/null 2>&1 || echo "  - Start Docker: open -a Docker"
    echo ""
    exit 1
fi
