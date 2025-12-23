# Version Comparison: Web vs GTK

## Quick Comparison

| Feature | Web Version | GTK Desktop Version |
|---------|-------------|---------------------|
| **Launch** | `./start.sh` or `python app.py` | `./start_gtk.sh` or `python app_gtk.py` |
| **Access** | Browser (<http://localhost:5000>) | Native desktop window |
| **Dependencies** | Flask, requests, python-dotenv | PyGObject, GTK3, requests, python-dotenv |
| **Remote Access** | ✅ Yes (over network) | ❌ Local only |
| **Mobile Friendly** | ✅ Yes | ❌ Desktop only |
| **System Integration** | ❌ Limited | ✅ Desktop entry, native menus |
| **Resource Usage** | Medium (needs browser) | Low (native app) |
| **Interface Style** | Modern gradient web UI | Native GTK3 desktop |
| **Tabs** | Single page with sections | Native tabbed interface |
| **Auto-refresh** | ✅ JavaScript timers | ✅ GLib timers |
| **Installation** | Simple (pip install) | Requires GTK3 system packages |
| **Platform** | Any OS with Python + Browser | Linux, BSD (GTK available) |

## Which Should I Use?

### Choose Web Version (`app.py`) if you

- Want to access from multiple devices
- Need mobile/tablet access
- Want remote monitoring (over LAN/VPN)
- Prefer not to install system packages
- Run on Windows/macOS without GTK

### Choose GTK Version (`app_gtk.py`) if you

- Prefer native desktop applications
- Want better system integration
- Use Linux as your primary OS
- Want lower resource usage
- Prefer tabbed interface
- Don't need remote access

## Can I Use Both?

**Yes!** Both versions use the same backend (`emby_client.py` and `config.py`), so you can:

1. Run both simultaneously (different ports for web version if needed)
2. Keep both installed and choose based on your needs
3. Use web version for remote access, GTK for local use

## Feature Parity

Both versions provide:

- ✅ Server status monitoring
- ✅ Current processing with progress bars
- ✅ Recently completed tasks
- ✅ Indexed media browsing
- ✅ Auto-refresh capabilities
- ✅ Same Emby API features

The main difference is the presentation layer!

## Installation Differences

### Web Version

```bash
# Simple pip install
pip install -r requirements.txt
./start.sh
```

### GTK Version

```bash
# Install system packages first
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0  # Ubuntu/Debian
# Then install Python deps
pip install -r requirements.txt
./start_gtk.sh
```

## Screenshots Comparison

### Web Version

- Gradient purple/pink background
- Card-based layout
- Inline progress bars
- Auto-refresh indicator with animation

### GTK Version

- Native GTK3 theme (follows system theme)
- Tabbed interface
- Native GTK widgets
- Status bar at bottom

## Performance

**Web Version:**

- Memory: ~50-100 MB (Flask + Browser)
- CPU: Low (only when refreshing)
- Network: HTTP requests to localhost:5000

**GTK Version:**

- Memory: ~30-50 MB (Python + GTK)
- CPU: Very low (native widgets)
- Network: Direct API calls (no localhost server)

## Development & Extensibility

Both versions share core logic:

- `emby_client.py` - Emby API wrapper
- `config.py` - Configuration management

You can extend either version independently or add features that benefit both!
