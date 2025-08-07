#!/bin/bash

# Auto-Newsletter Generator Runner Script

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.installed
    else
        echo "Error: Failed to install dependencies."
        exit 1
    fi
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ] && [ ! -f ".env" ]; then
    echo "Warning: OPENAI_API_KEY environment variable not set and .env file not found."
    echo "Please set your OpenAI API key:"
    read -p "API Key: " api_key
    echo "OPENAI_API_KEY=$api_key" > .env
fi

# Parse command line arguments
WEB_APP=false
CLI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --web)
            WEB_APP=true
            shift
            ;;
        --cli)
            CLI=true
            shift
            ;;
        *)
            # Pass remaining arguments to the Python script
            break
            ;;
    esac
done

# Run the application
if [ "$WEB_APP" = true ]; then
    echo "Starting web interface..."
    streamlit run src/web_app.py
elif [ "$CLI" = true ]; then
    echo "Starting CLI interface..."
    python -m src.cli "$@"
else
    echo "Starting newsletter generation..."
    python -m src.main "$@"
fi