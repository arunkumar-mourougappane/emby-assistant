#!/bin/bash

# Emby Helper - Version Launcher
# Choose between Web UI and GTK Desktop version

clear
echo "╔═══════════════════════════════════════╗"
echo "║    Emby Server Monitor Launcher      ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Which version would you like to run?"
echo ""
echo "  1) 🌐 Web Version (Browser-based)"
echo "     - Access from any device"
echo "     - URL: http://localhost:5000"
echo ""
echo "  2) 🖥️  GTK Desktop Version"
echo "     - Native desktop application"
echo "     - Better system integration"
echo ""
echo "  3) ❌ Exit"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting Web Version..."
        ./start.sh
        ;;
    2)
        echo ""
        echo "Starting GTK Desktop Version..."
        ./start_gtk.sh
        ;;
    3)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again."
        exit 1
        ;;
esac
