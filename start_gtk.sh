#!/bin/bash

# Emby Assistant GTK Desktop Application Startup Script

echo "====================================="
echo "  Emby Assistant (GTK Desktop)"
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

# Check for GTK3 development files
if pkg-config --exists gtk+-3.0; then
    echo "⚠️  GTK3 not found. Installing system dependencies..."
    echo ""
    
    if command -v apt-get &> /dev/null; then
        echo "Detected Debian/Ubuntu system"
        sudo apt-get update
        sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
    elif command -v dnf &> /dev/null; then
        echo "Detected Fedora system"
        sudo dnf install -y python3-gobject gtk3
    elif command -v pacman &> /dev/null; then
        echo "Detected Arch Linux system"
        sudo pacman -S --noconfirm python-gobject gtk3
    else
        echo "⚠️  Please install GTK3 and PyGObject manually for your system"
        echo "See: https://pygobject.readthedocs.io/en/latest/getting_started.html"
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv --system-site-packages
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q requests python-dotenv

echo ""
echo "Starting Emby Assistant GTK Application..."
echo ""
echo "Press Ctrl+C in this terminal to stop the application"
echo ""

# Run the GTK application
python app_gtk.py
