#!/bin/bash

# Emby Assistant Startup Script

echo "====================================="
echo "  Emby Assistant"
echo "====================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "Please edit the .env file with your Emby server details:"
    echo "  - EMBY_SERVER_URL (your Emby server address)"
    echo "  - EMBY_API_KEY (generate from Emby Dashboard -> Advanced -> API Keys)"
    echo ""
    read -p "Press Enter after you've configured .env file..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting Emby Assistant..."
echo "Access the dashboard at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
