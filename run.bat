@echo off
REM Auto-Newsletter Generator Runner Script for Windows

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist venv\.installed (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% EQU 0 (
        echo. > venv\.installed
    ) else (
        echo Error: Failed to install dependencies.
        exit /b 1
    )
)

REM Check for OpenAI API key
if not exist .env (
    if "%OPENAI_API_KEY%"=="" (
        echo Warning: OPENAI_API_KEY environment variable not set and .env file not found.
        echo Please set your OpenAI API key:
        set /p api_key=API Key: 
        echo OPENAI_API_KEY=%api_key%> .env
    )
)

REM Parse command line arguments
set WEB_APP=false
set CLI=false

:parse_args
if "%~1"=="" goto run_app
if "%~1"=="--web" (
    set WEB_APP=true
    shift
    goto parse_args
)
if "%~1"=="--cli" (
    set CLI=true
    shift
    goto parse_args
)

:run_app
REM Run the application
if "%WEB_APP%"=="true" (
    echo Starting web interface...
    streamlit run src/web_app.py
) else if "%CLI%"=="true" (
    echo Starting CLI interface...
    python -m src.cli %*
) else (
    echo Starting newsletter generation...
    python -m src.main %*
)