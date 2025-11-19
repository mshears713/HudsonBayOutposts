#!/bin/bash
#
# Test Runner Script for Hudson Bay Outposts
#
# This script provides convenient commands for running different test suites.
#
# Usage:
#   ./scripts/run_tests.sh [option]
#
# Options:
#   all          - Run all tests (default)
#   unit         - Run only unit tests
#   integration  - Run only integration tests
#   coverage     - Run tests with coverage report
#   fast         - Run fast tests only (skip slow tests)
#   verbose      - Run with verbose output
#   html         - Generate HTML test report
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Please run: pip install -r requirements-test.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

echo "=========================================="
echo "Hudson Bay Outposts Test Runner"
echo "=========================================="
echo ""

case "$TEST_TYPE" in
    all)
        print_info "Running all tests..."
        pytest tests/ -v --cov=src --cov=raspberry_pi --cov-report=term-missing
        ;;

    unit)
        print_info "Running unit tests only..."
        pytest tests/ -v -m unit --cov=src --cov=raspberry_pi --cov-report=term-missing
        ;;

    integration)
        print_info "Running integration tests only..."
        pytest tests/ -v -m integration
        ;;

    coverage)
        print_info "Running tests with detailed coverage report..."
        pytest tests/ -v --cov=src --cov=raspberry_pi \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-report=xml
        print_info "Coverage report generated in htmlcov/index.html"
        ;;

    fast)
        print_info "Running fast tests only (skipping slow tests)..."
        pytest tests/ -v -m "not slow" --cov=src --cov=raspberry_pi --cov-report=term-missing
        ;;

    verbose)
        print_info "Running all tests with verbose output..."
        pytest tests/ -vv -s --cov=src --cov=raspberry_pi --cov-report=term-missing
        ;;

    html)
        print_info "Running tests and generating HTML report..."
        pytest tests/ -v --html=test_report.html --self-contained-html \
            --cov=src --cov=raspberry_pi --cov-report=html
        print_info "Test report generated: test_report.html"
        print_info "Coverage report generated: htmlcov/index.html"
        ;;

    ci)
        print_info "Running CI test suite..."
        pytest tests/ -v --cov=src --cov=raspberry_pi \
            --cov-report=xml \
            --cov-report=term \
            --junitxml=junit.xml
        ;;

    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo ""
        echo "Available options:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run only unit tests"
        echo "  integration  - Run only integration tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  fast         - Run fast tests only (skip slow tests)"
        echo "  verbose      - Run with verbose output"
        echo "  html         - Generate HTML test report"
        echo "  ci           - Run CI test suite"
        exit 1
        ;;
esac

# Check test result
if [ $? -eq 0 ]; then
    echo ""
    print_info "✅ All tests passed!"
    exit 0
else
    echo ""
    print_error "❌ Some tests failed"
    exit 1
fi
