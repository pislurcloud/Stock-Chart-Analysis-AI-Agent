#!/bin/bash

# Stock Analysis AI - Phase 1 Setup Script
# This script installs dependencies and runs tests

echo "=================================================="
echo "  Stock Technical Analysis AI - Phase 1 Setup"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment (optional but recommended)
read -p "Do you want to create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    cd /home/claude/stock-analysis-ai/backend
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo "To activate it later, run: source /home/claude/stock-analysis-ai/backend/venv/bin/activate"
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd /home/claude/stock-analysis-ai/backend

pip install --upgrade pip --break-system-packages > /dev/null 2>&1

# Install from requirements.txt
pip install -r requirements.txt --break-system-packages

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Error installing dependencies${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo -e "${YELLOW}Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from .env.example${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file and add your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Run tests
echo ""
echo -e "${YELLOW}Running Phase 1 tests...${NC}"
echo ""

cd /home/claude/stock-analysis-ai/backend
python3 tests/test_phase1.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=================================================="
    echo "  ✓ Phase 1 Setup Complete!"
    echo "==================================================${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file and add your API keys"
    echo "2. Run the FastAPI server:"
    echo "   cd /home/claude/stock-analysis-ai/backend"
    echo "   python3 main.py"
    echo ""
    echo "3. Test the API at: http://localhost:8000"
    echo "   - Docs: http://localhost:8000/docs"
    echo "   - Health: http://localhost:8000/api/health"
    echo ""
else
    echo -e "${RED}✗ Tests failed. Please check the errors above.${NC}"
    exit 1
fi