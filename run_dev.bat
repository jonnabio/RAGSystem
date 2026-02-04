@echo off
echo Starting RAG System...

echo Starting Backend...
start "RAG Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python -m src.main"

echo Starting Frontend...
start "RAG Frontend" cmd /k "cd frontend && npm run dev"

echo Services allow a few seconds to initialize.
echo Backend: http://localhost:8001/docs
echo Frontend: http://localhost:3000
