# Documentation Index

Welcome to the Emby Helper documentation! This guide will help you find the information you need.

## 📚 Documentation Structure

### Getting Started

- **[README.md](../README.md)** - Main documentation with installation and usage
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide for immediate setup

### Version-Specific Guides

- **[README-GTK.md](README-GTK.md)** - Complete guide for GTK desktop version
- **[COMPARISON.md](COMPARISON.md)** - Web vs GTK version comparison

### Feature Documentation

- **[THUMBNAILS.md](THUMBNAILS.md)** - Thumbnail display feature details

### Project Information

- **[PROJECT.md](PROJECT.md)** - Complete project overview and file structure

## 🚀 Quick Navigation

### First Time Users

1. Start with [README.md](../README.md) for installation
2. Follow [QUICKSTART.md](QUICKSTART.md) for fast setup
3. Choose your version using [COMPARISON.md](COMPARISON.md)

### Web Version Users

1. [README.md](../README.md) - Installation and usage
2. [QUICKSTART.md](QUICKSTART.md) - Quick reference

### GTK Desktop Users

1. [README-GTK.md](README-GTK.md) - Complete GTK guide
2. [QUICKSTART.md](QUICKSTART.md) - Quick reference

### Developers & Contributors

1. [PROJECT.md](PROJECT.md) - Complete project structure
2. [THUMBNAILS.md](THUMBNAILS.md) - Feature implementation details

## 📖 Documentation by Topic

### Installation

- [Main Installation Guide](../README.md#installation)
- [GTK Installation](README-GTK.md#installation)
- [System Requirements](README-GTK.md#prerequisites)

### Configuration

- [Getting API Keys](../README.md#getting-an-emby-api-key)
- [Environment Variables](../README.md#configuration)
- [Advanced Settings](QUICKSTART.md#configuration-options)

### Usage

- [Web Version Usage](../README.md#usage)
- [GTK Version Usage](README-GTK.md#usage)
- [Features Overview](../README.md#features)

### Features

- [Server Status Monitoring](../README.md#features)
- [Task Processing](../README.md#features)
- [Media Indexing](../README.md#features)
- [Thumbnail Display](THUMBNAILS.md)

### Troubleshooting

- [Common Issues](../README.md#troubleshooting)
- [GTK-Specific Issues](README-GTK.md#troubleshooting)
- [Thumbnail Issues](THUMBNAILS.md#troubleshooting)

### Comparison & Decisions

- [Which Version to Use?](COMPARISON.md#which-should-i-use)
- [Feature Comparison Table](COMPARISON.md#quick-comparison)
- [Performance Comparison](COMPARISON.md#performance)

## 🔍 Search by Use Case

### "I want to monitor my Emby server from my browser"

→ Use the **Web Version**: [README.md](../README.md)

### "I want a native desktop application"

→ Use the **GTK Version**: [README-GTK.md](README-GTK.md)

### "I want to access from multiple devices"

→ Use the **Web Version**: [README.md](../README.md)

### "I can't decide which version to use"

→ Read the **Comparison**: [COMPARISON.md](COMPARISON.md)

### "I want to see movie posters"

→ Learn about **Thumbnails**: [THUMBNAILS.md](THUMBNAILS.md)

### "I need quick setup instructions"

→ Follow the **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

### "I want to understand the project structure"

→ Read the **Project Guide**: [PROJECT.md](PROJECT.md)

## 📝 Document Summaries

### README.md (Main)

Complete documentation including installation, configuration, features, and troubleshooting for both versions.

### QUICKSTART.md

Fast-track setup guide with minimal explanation. Perfect for experienced users.

### README-GTK.md

Comprehensive guide for the GTK desktop version including system requirements, installation, and GTK-specific features.

### COMPARISON.md

Side-by-side comparison of Web and GTK versions helping you choose the right one for your needs.

### THUMBNAILS.md

Technical documentation for the thumbnail feature including implementation details and troubleshooting.

### PROJECT.md

Project overview with complete file structure, configuration options, and development information.

## 🎯 Common Tasks

### Setup & Installation

```bash
# Quick setup
cp .env.example .env
nano .env  # Add your credentials
pip install -r requirements.txt
./launch.sh
```

See: [QUICKSTART.md](QUICKSTART.md)

### Running the Application

```bash
# Choose version interactively
./launch.sh

# Web version directly
./start.sh

# GTK version directly
./start_gtk.sh
```

See: [README.md](../README.md#usage)

### Getting Help

- Check [Troubleshooting](../README.md#troubleshooting)
- Review [GTK Issues](README-GTK.md#troubleshooting)
- See [Common Problems](QUICKSTART.md#troubleshooting)

## 📂 File Organization

```text
docs/
├── INDEX.md          # This file - Documentation index
├── QUICKSTART.md     # Quick start guide
├── README-GTK.md     # GTK version documentation
├── COMPARISON.md     # Version comparison
├── THUMBNAILS.md     # Feature documentation
└── PROJECT.md        # Project overview

../
├── README.md         # Main documentation
├── app.py           # Web application
├── app_gtk.py       # GTK application
└── ...              # Other project files
```

## 🔗 External Resources

- [Emby Server Documentation](https://emby.media/support.html)
- [Emby API Reference](https://dev.emby.media/)
- [GTK3 Documentation](https://gtk.org/)
- [PyGObject Guide](https://pygobject.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 📄 License & Support

This project is open source and available for personal use. See the [main README](../README.md) for more information.

---

**Quick Links:**
[Main README](../README.md) |
[Quick Start](QUICKSTART.md) |
[GTK Guide](README-GTK.md) |
[Comparison](COMPARISON.md) |
[Project Info](PROJECT.md)
