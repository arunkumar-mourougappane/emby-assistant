#!/bin/bash

# Emby Assistant Installation Script
# Installs environment for both Web UI and GTK Desktop versions

set -e  # Exit on error

echo "==========================================="
echo "  Emby Assistant Installer"
echo "==========================================="
echo ""

# 1. System Dependencies Check (GTK3)
echo "checking system dependencies..."
GTK_INSTALLED=false

if command -v pkg-config &> /dev/null && pkg-config --exists gtk+-3.0; then
    echo "✅ GTK3 found."
    GTK_INSTALLED=true
else
    echo "⚠️  GTK3 not found (Required for Desktop App)."
    read -p "Do you want to install system dependencies for GTK? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            echo "Installing APT packages..."
            sudo apt-get update
            sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 libcairo2-dev pkg-config python3-dev
        elif command -v dnf &> /dev/null; then
            echo "Installing DNF packages..."
            sudo dnf install -y python3-gobject gtk3 cairo-gobject-devel
        elif command -v pacman &> /dev/null; then
            echo "Installing Pacman packages..."
            sudo pacman -S --noconfirm python-gobject gtk3
        else
            echo "❌ Could not detect package manager. Please install GTK3 manually."
            # Continue anyway, maybe they just want Web UI
        fi
    else
        echo "Skipping GTK dependencies. Desktop app may not work."
    fi
fi

# 2. Virtual Environment Setup
echo ""
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    # Use system-site-packages to inherit system python-gi if installed there
    python3 -m venv venv --system-site-packages
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# 3. Install Python Dependencies
echo ""
echo "Installing Python libraries..."
source venv/bin/activate
pip install -q --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed."
else
    echo "⚠️  requirements.txt not found! Installing basics..."
    pip install requests python-dotenv flask
fi

# 4. Configuration Setup
echo ""
echo "Checking configuration..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from template."
        echo "Please edit .env with your EMBY_SERVER_URL and EMBY_API_KEY."
    fi
else
    echo "✅ Configuration found."
fi

# 5. Desktop Shortcut
echo ""
echo "Installing Desktop Shortcut..."
if [ -f "emby-monitor.desktop" ]; then
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    # Update Path in desktop file to current directory
    CURRENT_DIR=$(pwd)
    sed "s|Path=.*|Path=$CURRENT_DIR|" emby-monitor.desktop > "$DESKTOP_DIR/emby-monitor.desktop"
    sed -i "s|Exec=.*|Exec=$CURRENT_DIR/start_gtk.sh|" "$DESKTOP_DIR/emby-monitor.desktop"
    
    # Also link icon if needed (assuming icon/icon.png exists referenced in desktop file)
    
    echo "✅ Desktop entry installed to $DESKTOP_DIR/emby-monitor.desktop"
else
    echo "⚠️  emby-monitor.desktop not found. Skipping shortcut."
fi

echo ""
echo "==========================================="
echo "  Installation Complete!"
echo "==========================================="
echo ""
echo "To run the Web UI:"
echo "  ./start.sh"
echo ""
echo "To run the Desktop App:"
echo "  ./start_gtk.sh"
echo ""
