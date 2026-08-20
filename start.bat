@echo off
echo ================================================
echo   Resume Analyzer - Starting servers...
echo ================================================

set BASE=C:\Users\prade\OneDrive\Desktop\Resume Analyzer\resume-analyzer

echo.
echo [0/3] Running database migration...
call "%BASE%\backend\venv\Scripts\python.exe" "%BASE%\backend\migrate_db.py"
echo Migration done.

echo.
echo [1/3] Starting Backend on http://localhost:8000
start "Resume Analyzer - Backend" cmd /k "cd /d "%BASE%\backend" && venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"

echo Waiting for backend...
timeout /t 4 /nobreak > nul

echo.
echo [2/3] Starting Frontend on http://localhost:5173
start "Resume Analyzer - Frontend" cmd /k "cd /d "%BASE%\frontend" && npm run dev"

echo.
echo ================================================
echo   App         : http://localhost:5173
echo   AI Chatbot  : http://localhost:5173/chatbot
echo   Job Match   : http://localhost:5173/job-match
echo   Interview   : http://localhost:5173/interview/questions
echo   API Docs    : http://localhost:8000/docs
echo ================================================

timeout /t 6 /nobreak > nul
start http://localhost:5173
pause
