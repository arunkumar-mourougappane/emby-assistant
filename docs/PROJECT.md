# 📦 Emby Assistant - Project Overview

Complete monitoring solution for Emby Media Server with **two interfaces**: Web UI and GTK Desktop.

## 🎯 What This Does

Monitor your Emby server in real-time:

- **Server Status**: Version, OS, online status
- **Active Processing**: Current tasks with progress bars
- **Completed Tasks**: Recently finished jobs with duration
- **Indexed Media**: Browse recently added movies, shows, episodes
- **All Tasks**: Complete list of scheduled tasks

## 🚀 Quick Start (3 Steps)

```bash
# 1. Configure (first time only)
cp .env.example .env
nano .env  # Add your EMBY_SERVER_URL and EMBY_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch (choose your version)
./launch.sh
```

## 📁 Project Files

### Core Application Files

- **`emby_client.py`** - Emby API wrapper (shared by both versions)
- **`config.py`** - Configuration loader (shared by both versions)
- **`app.py`** - Flask web application (Browser UI)
- **`app_gtk.py`** - GTK desktop application (Native UI)

### Templates & UI

### Templates & UI

- **`templates/index.html`** - Web UI Dashboard
- **`templates/base.html`** - Base layout with navigation and scripts
- **`templates/cast.html`** - Cast explorer page
- **`templates/media.html`** - Media library browser

### Launchers & Scripts

- **`launch.sh`** - Interactive launcher (choose version)
- **`start.sh`** - Web version launcher
- **`start_gtk.sh`** - GTK version launcher

### Configuration

- **`.env.example`** - Configuration template
- **`.env`** - Your actual config (create from example)
- **`requirements.txt`** - Python dependencies
- **`.gitignore`** - Git ignore rules

### Desktop Integration

- **`emby-monitor.desktop`** - Desktop entry file for app menu

### Documentation

- **`README.md`** - Main documentation
- **`LICENSE`** - MIT License
- **`CONTRIBUTING.md`** - Contribution guidelines
- **`docs/`** - Documentation folder
  - **`INDEX.md`** - Documentation index
  - **`README.md`** - Docs folder overview
  - **`QUICKSTART.md`** - Quick reference guide
  - **`README-GTK.md`** - GTK version specific docs
  - **`COMPARISON.md`** - Web vs GTK comparison
  - **`THUMBNAILS.md`** - Thumbnail feature docs
  - **`PROJECT.md`** - This file

## 🎨 Two Versions, Same Power

| Feature          | Web Version               | GTK Desktop             |
| ---------------- | ------------------------- | ----------------------- |
| **Command**      | `./start.sh`              | `./start_gtk.sh`        |
| **Access**       | Browser at localhost:5000 | Native window           |
| **Best For**     | Remote access, mobile     | Local use, low resource |
| **Dependencies** | Flask                     | PyGObject + GTK3        |

Both versions provide identical functionality - just different interfaces!

## 🔧 Configuration

Edit `.env` file:

```bash
# Required
EMBY_SERVER_URL=http://your-emby-server:8096
EMBY_API_KEY=your_api_key_here

# Optional
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

**Getting an API Key:**

1. Open Emby web interface
2. Dashboard → Advanced → API Keys
3. Click "+ New API Key"
4. Name it "Emby Assistant"
5. Copy key to `.env` file

## 📊 Features Breakdown

### Server Status Monitor

- Real-time connection indicator
- Server name, version, OS info
- Manual refresh button

### Current Processing (Auto-refresh: 5s)

- Active tasks with progress bars
- Task category and description
- Start time and state
- Color-coded badges

### Completed Tasks

- Last 15 completed jobs
- Execution duration
- Completion timestamps
- Success/failure status

### Indexed Media

- Recently added content
- Choose 50/100/200 items
- Movies, series, episodes
- Full file paths
- Added timestamps

### All Tasks

- Complete scheduled task list
- Current state
- Last execution info
- Progress for running tasks

## 🛠️ System Requirements

### Both Versions

- Python 3.8+
- Emby Server with API access
- Linux, macOS, or Windows

### Web Version Only

- Any modern web browser

### GTK Version Only (Additional)

- GTK3 (gtk+-3.0)
- PyGObject (python3-gi)
- Linux or BSD recommended

## 📚 Documentation Quick Links

- **[README.md](../README.md)** - Full documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[README-GTK.md](README-GTK.md)** - GTK version details
- **[COMPARISON.md](COMPARISON.md)** - Version comparison
- **[INDEX.md](INDEX.md)** - Complete documentation index

## 🎓 Usage Examples

### Web Version

```bash
# Start web server
./start.sh

# Access from browser
http://localhost:5000

# Access from other device (if firewall allows)
http://your-ip:5000
```

### GTK Version

```bash
# Launch desktop app
./start_gtk.sh

# Or install to applications menu
cp emby-monitor.desktop ~/.local/share/applications/
# Then launch from app menu
```

### Both at Once

```bash
# Terminal 1: Web version
./start.sh

# Terminal 2: GTK version
./start_gtk.sh

# They share the same .env config!
```

## 🔌 API Endpoints (Web Version)

When running web version, these endpoints are available:

- `GET /` - Main dashboard
- `GET /api/status` - Server status
- `GET /api/current-processing` - Active tasks
- `GET /api/completed-tasks` - Recent completions
- `GET /api/indexed-media?limit=50` - Recent media
- `GET /api/all-tasks` - All scheduled tasks

## 🤝 Contributing Ideas

Want to extend this project? Ideas:

- Add notifications (desktop/email)
- System tray icon for GTK version
- Dark mode toggle
- Export task history to CSV
- Email alerts for failures
- Mobile app version
- Docker container
- Multiple server support

## ⚠️ Troubleshooting

**Can't connect to server:**

- Check `EMBY_SERVER_URL` in `.env`
- Verify Emby is running
- Test: `curl http://your-server:8096/emby/System/Info`

**GTK version won't start:**

- Install GTK3: `sudo apt-get install python3-gi gir1.2-gtk-3.0`
- Use system packages: `python3 -m venv venv --system-site-packages`

**No data showing:**

- Verify API key is correct
- Check Emby has media libraries
- Look at terminal output for errors

## 📄 License

Open source - free for personal use

## ⚖️ Disclaimer

Unofficial tool - not affiliated with Emby

---

**Made with ❤️ for Emby users**

Start monitoring: `./launch.sh`
