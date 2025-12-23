# Emby Assistant

Monitor your Emby server with real-time information about server status, pending jobs, currently processing media, and recently indexed content.

> 📚 **Documentation**: See [docs/](docs/) folder for detailed guides | Quick navigation: [docs/INDEX.md](docs/INDEX.md)

**Two versions available:**

- **Web UI** ([app.py](app.py)) - Flask web application accessible from any browser
- **GTK Desktop** ([app_gtk.py](app_gtk.py)) - Native GTK3 desktop application ([Documentation](docs/README-GTK.md))

## Features

- **Server Status**: View server information including version, OS, online status, and live server time
- **Cast Explorer**: Browse and search active persons (actors, directors) with bio and credits
- **Movies Browser**: Filter movies by library with improved visual layout
- **Current Processing**: Monitor active tasks with real-time progress bars
- **Recently Completed Tasks**: See recently finished jobs with duration
- **Indexed Media**: Browse recently added media items to your library
  - **Thumbnails**: Movies and videos display poster images automatically
- **Auto-refresh**: Automatically updates processing status every 5 seconds
- **Modern UI**: Clean, responsive web interface with Dark Mode support

## Prerequisites

- Python 3.8 or higher
- Emby Server with API access
- Emby API Key (see setup instructions below)

## Installation

1. Clone or download this repository

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Emby connection:

   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your Emby server details:
   - `EMBY_SERVER_URL`: Your Emby server URL (e.g., `http://192.168.1.100:8096`)
   - `EMBY_API_KEY`: Your API key (see below how to generate)

### Getting an Emby API Key

1. Open your Emby web interface
2. Go to **Dashboard** (hamburger menu → Dashboard)
3. Click on **Advanced** in the left sidebar
4. Click on **API Keys**
5. Click **+ New API Key**
6. Enter an application name (e.g., "Emby Assistant")
7. Copy the generated API key to your `.env` file

## Usage

### Web Version (Browser-based)

1. Start the application:

```bash
python app.py
# or use the startup script
./start.sh
```

1. Open your web browser and navigate to:

```text
http://localhost:5000
```

### GTK Desktop Version (Native Application)

1. Start the desktop application:

   ```bash
   python app_gtk.py
   # or use the GTK launcher
   ./start_gtk.sh
   ```

2. The GTK window will open automatically

For detailed GTK instructions, see [README-GTK.md](docs/README-GTK.md)

### What You'll See

Both versions display:

- Server status and information
- Currently processing media with progress
- Recently completed tasks
- Recently indexed media items

## Configuration

You can configure the application using environment variables in the `.env` file:

- `EMBY_SERVER_URL`: Emby server URL (default: `http://localhost:8096`)
- `EMBY_API_KEY`: Your Emby API key (required)

## Project Structure

   ```text
   emby-helper/
   ├── app.py              # Flask web application
   ├── app_gtk.py          # GTK desktop application
   ├── emby_client.py      # Emby API client (shared by both versions)
   ├── config.py           # Configuration loader (shared)
   ├── templates/
   │   ├── index.html      # Dashboard template
   │   ├── base.html       # Base template with nav
   │   ├── cast.html       # Cast page template
   │   └── media.html      # Media library template
   ├── icon/               # Application icons (various sizes)
   ├── docs/               # Documentation
   │   ├── QUICKSTART.md   # Quick start guide
   │   ├── README-GTK.md   # GTK version docs
   │   ├── COMPARISON.md   # Web vs GTK comparison
   │   ├── PROJECT.md      # Project overview
   │   └── THUMBNAILS.md   # Thumbnail feature docs
   ├── requirements.txt    # Python dependencies
   ├── .env.example        # Example environment configuration
   ├── start.sh            # Web version launcher
   ├── start_gtk.sh        # GTK version launcher
   ├── launch.sh           # Interactive launcher
   ├── emby-monitor.desktop # Desktop entry file
   └── README.md           # This file
   ```

## API Endpoints

The application provides the following API endpoints:

- `GET /api/status` - Server status information
- `GET /api/server-time` - Live server time
- `GET /api/current-processing` - Currently processing media
- `GET /api/completed-tasks` - Recently completed tasks
- `GET /api/indexed-media?limit=50` - Recently indexed media
- `GET /api/all-tasks` - All scheduled tasks
- `GET /api/cast` - List of cast members
- `GET /api/person/<id>` - Person details (Bio, Birth info)
- `GET /api/person/<id>/credits` - Person movie credits

## Troubleshooting

### Cannot connect to Emby server

- Verify `EMBY_SERVER_URL` is correct in your `.env` file
- Check that your Emby server is running
- Ensure the API key is valid
- Check firewall settings if accessing remotely

### No data showing

- Make sure the API key has proper permissions
- Check that Emby has media libraries configured
- Verify there are scheduled tasks in Emby

### Port 5000 already in use

Edit `app.py` and change the port number in the last line:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to different port
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by Emby.

---

**Documentation:** [docs/INDEX.md](docs/INDEX.md) |
**Quick Start:** [docs/QUICKSTART.md](docs/QUICKSTART.md) |
**GTK Guide:** [docs/README-GTK.md](docs/README-GTK.md) |
**Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md)
