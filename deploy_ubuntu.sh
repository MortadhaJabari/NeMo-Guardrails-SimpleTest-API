#!/bin/bash

# Ubuntu VM Deployment Script
# Run this script on your Ubuntu VM after copying the project files

echo "🚀 Deploying NeMo Guardrails API on Ubuntu VM..."

# Ensure we have Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt update
    sudo apt install docker.io docker-compose -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "⚠️  Please log out and back in, then run this script again"
    exit 1
fi

# Build and run the API
echo "Building the Docker image..."
docker build -f Dockerfile-simple -t nemo-guardrails-api .

echo "Starting the API service..."
docker-compose up -d

# Wait for the service to start
echo "Waiting for service to start..."
sleep 10

# Test the API
echo "Testing the API..."
curl -f http://localhost:5000/health || {
    echo "❌ API health check failed"
    docker-compose logs
    exit 1
}

echo "✅ NeMo Guardrails API deployed successfully!"
echo "🌐 API is running on: http://$(hostname -I | awk '{print $1}'):5000"
echo "📋 Health check: http://$(hostname -I | awk '{print $1}'):5000/health"
echo "🔍 Simple validation: http://$(hostname -I | awk '{print $1}'):5000/validate/simple"

# Show running containers
echo -e "\n📦 Running containers:"
docker ps

echo -e "\n📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
