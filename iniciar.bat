@echo off

echo Iniciando servidor FastAPI...
start cmd /k python -m uvicorn app.main:app --reload

:loop
curl http://127.0.0.1:8000 >nul 2>&1
if errorlevel 1 (
    timeout /t 1 >nul
    goto loop
)
echo abriendo navegador
start msedge http://127.0.0.1:8000

exit