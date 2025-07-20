#!/bin/bash

echo "Setting up Rice Mill AI System..."

# Copy environment file
cp .env.example .env
echo "✓ Environment file created"

# Build and start services
docker-compose build
echo "✓ Docker images built"

docker-compose up -d
echo "✓ Services started"

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
docker-compose exec backend python -c "from app import app; from extensions import db; app.app_context().push(); db.create_all()"
echo "✓ Database initialized"

echo "Setup complete! Access the application at http://localhost:3000"