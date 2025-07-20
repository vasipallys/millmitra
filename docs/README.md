# Rice Mill AI - Documentation

## Quick Start
1. Run `./scripts/setup.sh` to initialize the project
2. Access the application at http://localhost:3000
3. Default login: admin/admin123

## Architecture
- Frontend: React + Vite + Material-UI
- Backend: Python Flask + SQLAlchemy
- AI Services: FastAPI + LangChain + Google Gemini
- Database: PostgreSQL
- Cache: Redis
- Real-time: WebSocket

## Development
- `./scripts/dev.sh` - Start development environment
- `docker-compose logs [service]` - View service logs
- `docker-compose exec [service] bash` - Access service shell

## API Documentation
- Backend API: http://localhost:5000/api/docs
- AI Services: http://localhost:8000/docs