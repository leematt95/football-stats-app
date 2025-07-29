#!/usr/bin/env bash
# lint.sh - Comprehensive linting script for the football stats application

set -e  # Exit on any error

echo "🔍 Starting comprehensive code linting..."
echo "=========================================="

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

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No virtual environment detected. Installing packages globally..."
    print_warning "Consider activating your virtual environment first."
fi

# Install linting dependencies if not present
print_status "Checking for linting dependencies..."
pip install -q mypy flake8 bandit black isort || {
    print_error "Failed to install linting dependencies"
    exit 1
}

# Initialize error tracking
LINT_ERRORS=0

echo ""
print_status "Running Black (code formatter)..."
echo "-----------------------------------"
if black --check --diff app/ import_players.py; then
    print_success "Black: Code formatting is consistent ✅"
else
    print_warning "Black: Code formatting issues found. Run 'black app/ import_players.py' to fix"
    LINT_ERRORS=$((LINT_ERRORS + 1))
fi

echo ""
print_status "Running isort (import sorting)..."
echo "----------------------------------"
if isort --check-only --diff app/ import_players.py; then
    print_success "isort: Import order is correct ✅"
else
    print_warning "isort: Import order issues found. Run 'isort app/ import_players.py' to fix"
    LINT_ERRORS=$((LINT_ERRORS + 1))
fi

echo ""
print_status "Running Flake8 (style and syntax)..."
echo "-------------------------------------"
if flake8 app/ import_players.py; then
    print_success "Flake8: No style or syntax issues found ✅"
else
    print_error "Flake8: Style/syntax issues found ❌"
    LINT_ERRORS=$((LINT_ERRORS + 1))
fi

echo ""
print_status "Running MyPy (type checking)..."
echo "--------------------------------"
if mypy app/ import_players.py; then
    print_success "MyPy: No type errors found ✅"
else
    print_warning "MyPy: Type checking issues found ⚠️"
    LINT_ERRORS=$((LINT_ERRORS + 1))
fi

echo ""
print_status "Running Bandit (security analysis)..."
echo "--------------------------------------"
if bandit -r app/ import_players.py -f txt; then
    print_success "Bandit: No security issues found ✅"
else
    print_warning "Bandit: Security issues found ⚠️"
    LINT_ERRORS=$((LINT_ERRORS + 1))
fi

echo ""
echo "=========================================="
if [ $LINT_ERRORS -eq 0 ]; then
    print_success "🎉 All linting checks passed! Your code is clean."
    exit 0
else
    print_warning "⚠️  Linting completed with $LINT_ERRORS tool(s) reporting issues."
    print_status "Run the suggested commands above to fix formatting issues."
    echo ""
    echo "Quick fix commands:"
    echo "  black app/ import_players.py      # Fix formatting"
    echo "  isort app/ import_players.py      # Fix import order"
    echo "  flake8 app/ import_players.py     # Check style/syntax"
    echo "  mypy app/ import_players.py       # Check types"
    echo "  bandit -r app/ import_players.py  # Check security"
    exit 1
fi
