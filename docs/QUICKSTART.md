# Quick Start Guide

## 🚀 Getting Started

### 1. Installation (Recommended)

Run the automated installer which handles dependencies and configuration for both versions:

```bash
./install.sh
```

### 2. Launch

**Option 1: Interactive Launcher** (Recommended)

```bash
./launch.sh
```

This will let you choose between Web or GTK version.

**Option 2: Web Version** (Browser-based)

```bash
./start.sh
```

Access at: <http://localhost:5000>

**Option 3: GTK Desktop Version** (Native app)

```bash
./start_gtk.sh
```

Desktop window opens automatically.

See [COMPARISON.md](COMPARISON.md) for version differences.

### Manual Installation

If you prefer to install manually:

**For Web Version:**

```bash
pip install -r requirements.txt
```

**For GTK Version (Linux):**
Ensure GTK3 is installed (via apt/dnf/pacman) then run:

```bash
pip install -r requirements.txt
```

### 2. Configure Emby Connection

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your details:

```
EMBY_SERVER_URL=http://your-emby-server:8096
EMBY_API_KEY=your_api_key_here
```

**To get an API Key:**

1. Open Emby web interface
2. Dashboard → Advanced → API Keys
3. Click "+ New API Key"
4. Name it "Emby Assistant" and copy the key

### 3. Run the Application

**Option A - Interactive launcher (choose version):**

```bash
./launch.sh
```

**Option B - Web version directly:**

```bash
./start.sh
# or
python app.py
```

**Option C - GTK desktop version:**

```bash
./start_gtk.sh
# or
python app_gtk.py
```

### 4. Access the Dashboard

**Web Version:** Open your browser at **<http://localhost:5000>**

**GTK Version:** Desktop window opens automatically

## 📊 Features

### Server Status

- Server name, version, and OS
- Real-time online/offline indicator

### Current Processing

- Active tasks with progress bars
- Auto-refreshes every 5 seconds
- Shows task category and details

### Recently Completed Tasks

- Last 15 completed tasks
- Duration and completion time
- Task category and status

### Indexed Media

- Recently added media items
- Switch between 50 and 100 items
- Shows movies, series, and episodes
- Full path information

## 🛠️ Configuration Options

Create or edit `.env` file:

```bash
# Required
EMBY_SERVER_URL=http://localhost:8096
EMBY_API_KEY=your_key_here

# Optional
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
PROCESSING_REFRESH_INTERVAL=5
STATUS_REFRESH_INTERVAL=30
```

## 🔧 Troubleshooting

### Can't connect to Emby

- Check `EMBY_SERVER_URL` is correct
- Verify Emby server is running
- Check firewall settings

### API Key not working

- Regenerate API key in Emby
- Make sure there are no extra spaces in `.env`

### Port already in use

Change port in `.env`:

```
FLASK_PORT=5001
```

## 📁 Project Structure

```
emby-helper/
├── app.py              # Main Flask application
├── emby_client.py      # Emby API wrapper
├── config.py           # Configuration loader
├── templates/
│   └── index.html      # Web UI
├── requirements.txt    # Python dependencies
├── .env               # Your configuration (not in git)
├── .env.example       # Configuration template
├── start.sh           # Easy startup script
└── README.md          # Full documentation
```

## 🎯 API Endpoints

You can also use these programmatically:

- `GET /api/status` - Server information
- `GET /api/current-processing` - Active tasks
- `GET /api/completed-tasks` - Recent completions
- `GET /api/indexed-media?limit=50` - Recent media
- `GET /api/all-tasks` - All scheduled tasks

## 💡 Tips

1. **Auto-refresh**: The dashboard automatically refreshes processing tasks
2. **Manual refresh**: Click "Refresh" buttons for instant updates
3. **View limits**: Toggle between 50 and 100 items in indexed media
4. **Progress bars**: Watch media processing in real-time

## 📝 Notes

- This tool uses the official Emby API
- Read-only operations (doesn't modify your server)
- Works with Emby Server 4.x and later
