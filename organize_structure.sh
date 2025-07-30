#!/bin/bash

# Project Structure Reorganization Script
# Creates a clean, logical structure for the Football Stats API

echo "🔧 Reorganizing Football Stats API Project Structure..."

# Create logical directory structure
mkdir -p {src,tests,deployment,documentation}

# Move application code to src/
echo "📁 Moving application code to src/..."
if [ -d "app" ]; then
    mv app src/ 2>/dev/null || echo "app already in place"
fi

# Move test files to tests/
echo "🧪 Moving test files to tests/..."
mv test_*.py tests/ 2>/dev/null || echo "test files already organized"

# Move deployment files to deployment/
echo "🚀 Moving deployment files to deployment/..."
mv docker-compose.yml deployment/ 2>/dev/null || echo "docker-compose.yml already in deployment/"
mv dockerfile deployment/Dockerfile 2>/dev/null || echo "dockerfile already organized"
mv openshift-deployment.yaml deployment/ 2>/dev/null || echo "openshift files already organized"
mv entrypoint.sh deployment/ 2>/dev/null || echo "entrypoint.sh already organized"

# Move documentation to documentation/
echo "📚 Moving documentation to documentation/..."
if [ -d "docs" ]; then
    mv docs/* documentation/ 2>/dev/null || echo "docs already moved"
    rmdir docs 2>/dev/null || echo "docs directory still has content"
fi

# Keep root level clean with only essential files
echo "✨ Root level organization complete"

echo "✅ Project reorganization complete!"
echo "📊 Generating project tree..."
