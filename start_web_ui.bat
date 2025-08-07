@echo off
echo Starting AI Newsletter Generator Web Interface...
echo.

REM Change to the project directory
cd /d "e:\AuraFarming\Project4"

REM Activate virtual environment
call .\venv\Scripts\activate.bat

REM Start Streamlit app
echo Opening web interface at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run src/web_app.py --server.port 8501

pause
