@echo off
REM Simple batch file to run the newsletter generator

echo Starting Auto-Newsletter Generator...
echo.

REM Change to the project directory
cd /d "e:\AuraFarming\Project4"

REM Activate virtual environment
call .\venv\Scripts\activate.bat

REM Check what mode to run
if "%1"=="--test" (
    echo Running in TEST mode ^(offline, no OpenAI API calls^)...
    python test_run_offline.py
) else if "%1"=="--web" (
    echo Starting WEB interface...
    python -m src.web_app
) else if "%1"=="--cli" (
    echo Starting CLI interface...
    python -m src.cli
) else (
    echo Running normal mode ^(requires OpenAI API key^)...
    python -m src.main
)

echo.
echo Newsletter generation completed!
pause
