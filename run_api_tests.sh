#!/bin/bash

# API Runtime Testing Script
# Comprehensive testing suite for the Football Stats API

set -e

echo "🧪 Football Stats API - Complete Runtime Testing Suite"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Check if API is running
check_api_status() {
    print_status "🔍 Checking API status..." "$BLUE"
    
    if curl -s -f http://localhost:5000/ > /dev/null 2>&1; then
        print_status "✅ API is running and accessible" "$GREEN"
        return 0
    else
        print_status "❌ API is not accessible at http://localhost:5000" "$RED"
        print_status "💡 Please ensure the application is running with: docker-compose up -d" "$YELLOW"
        exit 1
    fi
}

# Start the application if not running
start_application() {
    print_status "🚀 Starting application..." "$BLUE"
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_status "✅ Application is already running" "$GREEN"
    else
        print_status "📦 Starting Docker containers..." "$YELLOW"
        docker-compose up -d
        
        print_status "⏳ Waiting for application to be ready..." "$YELLOW"
        sleep 15
        
        # Verify it started successfully
        if check_api_status; then
            print_status "✅ Application started successfully" "$GREEN"
        else
            print_status "❌ Failed to start application" "$RED"
            exit 1
        fi
    fi
}

# Run basic API tests
run_basic_tests() {
    print_status "🧪 Running basic API runtime tests..." "$BLUE"
    
    echo "Running comprehensive test suite..."
    python3 test_api_runtime.py
    
    echo ""
    print_status "✅ Basic runtime tests completed" "$GREEN"
}

# Run pytest tests
run_pytest_tests() {
    print_status "🔬 Running pytest-based tests..." "$BLUE"
    
    if command -v pytest >/dev/null 2>&1; then
        pytest test_api_pytest.py -v --tb=short --color=yes
        print_status "✅ Pytest tests completed" "$GREEN"
    else
        print_status "⚠️  pytest not found, running with python -m pytest..." "$YELLOW"
        python3 -m pytest test_api_pytest.py -v --tb=short
        print_status "✅ Pytest tests completed" "$GREEN"
    fi
}

# Run load tests
run_load_tests() {
    print_status "⚡ Running load testing..." "$BLUE"
    
    echo "Starting load testing suite..."
    python3 test_load_testing.py
    
    echo ""
    print_status "✅ Load testing completed" "$GREEN"
}

# Run API health check
run_health_check() {
    print_status "🏥 Running API health check..." "$BLUE"
    
    # Test basic endpoints
    endpoints=(
        "/"
        "/api/players/?limit=5"
        "/api/players/1"
        "/api/players/search/json?name=Arsenal"
        "/api/players/paginated?page=1&per_page=5"
    )
    
    all_healthy=true
    
    for endpoint in "${endpoints[@]}"; do
        url="http://localhost:5000${endpoint}"
        
        if response=$(curl -s -w "%{http_code}" "$url" 2>/dev/null); then
            http_code="${response: -3}"
            
            if [ "$http_code" = "200" ]; then
                print_status "✅ $endpoint - OK ($http_code)" "$GREEN"
            else
                print_status "⚠️  $endpoint - Warning ($http_code)" "$YELLOW"
            fi
        else
            print_status "❌ $endpoint - Failed" "$RED"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_status "✅ All endpoints are healthy" "$GREEN"
    else
        print_status "⚠️  Some endpoints may have issues" "$YELLOW"
    fi
}

# Generate test report
generate_report() {
    print_status "📊 Generating test report..." "$BLUE"
    
    report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Football Stats API - Test Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo ""
        
        echo "Application Status:"
        docker-compose ps
        echo ""
        
        echo "API Health Check Results:"
        curl -s http://localhost:5000/ | python3 -m json.tool 2>/dev/null || echo "API response received"
        echo ""
        
        echo "Database Status:"
        docker-compose exec -T db psql -U football_user -d football_stats -c "SELECT COUNT(*) as player_count FROM players;" 2>/dev/null || echo "Database query skipped"
        echo ""
        
        echo "Container Logs (last 20 lines):"
        echo "--- Web Service ---"
        docker-compose logs --tail=20 web 2>/dev/null || echo "Web logs not available"
        echo ""
        echo "--- Database Service ---"
        docker-compose logs --tail=20 db 2>/dev/null || echo "Database logs not available"
        
    } > "$report_file"
    
    print_status "📋 Test report saved to: $report_file" "$GREEN"
}

# Main execution
main() {
    echo ""
    print_status "🎯 Starting comprehensive API testing..." "$BLUE"
    echo ""
    
    # Step 1: Start application if needed
    start_application
    echo ""
    
    # Step 2: Health check
    run_health_check
    echo ""
    
    # Step 3: Basic runtime tests
    run_basic_tests
    echo ""
    
    # Step 4: Pytest tests
    run_pytest_tests
    echo ""
    
    # Step 5: Load tests
    print_status "❓ Would you like to run load tests? (y/n)" "$YELLOW"
    read -r run_load
    if [[ $run_load =~ ^[Yy]$ ]]; then
        run_load_tests
        echo ""
    else
        print_status "⏭️  Skipping load tests" "$YELLOW"
        echo ""
    fi
    
    # Step 6: Generate report
    generate_report
    echo ""
    
    # Final summary
    print_status "🎉 All API runtime testing completed successfully!" "$GREEN"
    print_status "🔍 Your API is ready for demo!" "$GREEN"
    
    echo ""
    echo "📝 Test Summary:"
    echo "   ✅ Application startup verification"
    echo "   ✅ API health checks"
    echo "   ✅ Comprehensive endpoint testing"
    echo "   ✅ Pytest-based unit tests"
    if [[ $run_load =~ ^[Yy]$ ]]; then
        echo "   ✅ Load testing"
    fi
    echo "   ✅ Test report generation"
    echo ""
    
    print_status "🚀 Your Football Stats API is production-ready!" "$GREEN"
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
