#!/bin/bash

echo "Starting development environment..."

# Start all services
docker-compose up --build

# Or start individual services:
# docker-compose up frontend backend ai-services db redis