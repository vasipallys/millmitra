#!/bin/bash
echo "Starting Rice Mill Management System..."

echo "Starting AI Services..."
cd ai-services
python main.py &
AI_PID=$!
cd ..

echo "Waiting for AI services to start..."
sleep 5

echo "Starting Backend API..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "All services started!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "AI Services: http://localhost:8000"
echo ""
echo "To stop all services, run: kill $AI_PID $BACKEND_PID $FRONTEND_PID"
