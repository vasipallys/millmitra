@echo off
echo Starting Rice Mill Management System...

echo Starting AI Services...
cd ai-services
start "AI Services" python main.py
cd ..

echo Waiting for AI services to start...
timeout /t 5

echo Starting Backend API...
cd backend
start "Backend API" python app.py
cd ..

echo Starting Frontend...
cd frontend
start "Frontend" npm run dev

echo All services started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo AI Services: http://localhost:8000
pause
