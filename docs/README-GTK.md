# Emby Helper - GTK Desktop Version

A native GTK3 desktop application for monitoring your Emby server with a beautiful, responsive interface.

## Features

- **Native Desktop Experience**: Full GTK3 desktop application
- **Tabbed Interface**: 
  - 🔄 Current Processing - Real-time task monitoring with progress bars
  - ✅ Completed Tasks - Recently finished jobs
  - 🎬 Indexed Media - Browse recently added content (50/100/200 items)
  - 📋 All Tasks - View all scheduled tasks
- **Auto-Refresh**: Processing updates every 5 seconds, status every 30 seconds
- **Server Status Bar**: Live server information at the top
- **Modern UI**: Clean GTK3 interface with color-coded badges

## Prerequisites

### System Requirements

- Python 3.8 or higher
- GTK3 (gtk+-3.0)
- PyGObject (python3-gi)
- Emby Server with API access

### Installing GTK3 Dependencies

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk3
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk3
```

**Other Systems:**
See: https://pygobject.readthedocs.io/en/latest/getting_started.html

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Emby connection:
```bash
cp .env.example .env
nano .env
```

4. Add your Emby server details to `.env`:
   - `EMBY_SERVER_URL`: Your Emby server URL
   - `EMBY_API_KEY`: Your API key (Dashboard → Advanced → API Keys)

## Running the Application

### Option 1: Using the Launcher Script (Recommended)
```bash
./start_gtk.sh
```

This script will:
- Check for GTK3 installation
- Set up virtual environment
- Install dependencies
- Launch the application

### Option 2: Direct Launch
```bash
python app_gtk.py
```

### Option 3: Desktop Entry
Install the desktop entry for your applications menu:
```bash
cp emby-monitor.desktop ~/.local/share/applications/
```

Then launch "Emby Server Monitor" from your applications menu.

## Usage

### Main Window

The application opens with a header showing:
- **Server Status**: Green indicator when connected
- **Server Info**: Name, version, and OS
- **Refresh Button**: Manually refresh all data

### Tabs

**🔄 Current Processing**
- Shows active tasks with real-time progress
- Progress bars update automatically
- Task categories and descriptions
- Auto-refreshes every 5 seconds

**✅ Completed Tasks**
- Recently completed jobs
- Execution duration
- Completion timestamps

**🎬 Indexed Media**
- Recently added movies, series, and episodes
- Dropdown to select 50, 100, or 200 items
- Full file paths
- Color-coded by media type

**📋 All Tasks**
- Complete list of scheduled tasks
- Current state and progress
- Last execution information

### Status Bar

The bottom status bar shows:
- Last action performed
- Timestamp of last update

## Keyboard Shortcuts

- `Ctrl+R`: Refresh all data (when focused on refresh button)
- `Ctrl+Q` or `Alt+F4`: Close application
- `Ctrl+Tab`: Switch between tabs

## Comparison: GTK vs Web Version

### GTK Desktop Version (app_gtk.py)
✅ Native desktop application
✅ No web browser required
✅ System tray integration ready
✅ Faster startup
✅ Better system integration
✅ Tabbed interface

### Web Version (app.py)
✅ Access from any device
✅ Mobile-friendly
✅ No installation on client machines
✅ Remote access possible
✅ Works on any OS with browser

Choose the version that fits your use case!

## Troubleshooting

### GTK3 Not Found
Install GTK3 development files for your system (see Prerequisites above).

### PyGObject Installation Fails
On some systems, you need to use system packages:
```bash
# Use --system-site-packages when creating venv
python3 -m venv venv --system-site-packages
```

### Application Won't Start
1. Check `.env` file exists and has valid credentials
2. Verify Emby server is running
3. Test connection: `curl http://your-emby-server:8096/emby/System/Info`

### No Data Showing
- Verify API key has permissions
- Check Emby has media libraries configured
- Look for errors in terminal output

## Development

### File Structure
```
emby-helper/
├── app_gtk.py           # GTK desktop application
├── emby_client.py       # Emby API client (shared)
├── config.py            # Configuration (shared)
├── start_gtk.sh         # GTK launcher script
├── emby-monitor.desktop # Desktop entry file
└── README-GTK.md        # This file
```

### Running in Development Mode
```bash
# Enable debug output
export FLASK_DEBUG=True
python app_gtk.py
```

## License

This project is open source and available for personal use.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by Emby.
