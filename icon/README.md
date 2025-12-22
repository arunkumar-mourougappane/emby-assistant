# Emby Helper Icons

This folder contains the application icons in various sizes and formats.

## Available Icons

### Original High-Resolution Icons (1024x1024)
- **emby-assistant-rounded.png** - Rounded square icon (944 KB)
- **emby-assistant-spherical.png** - Circular/spherical icon (891 KB)

### Generated Icon Sizes
- **emby-assistant-256.png** - 256x256 px (73 KB)
- **emby-assistant-128.png** - 128x128 px (22 KB)
- **emby-assistant-64.png** - 64x64 px (7 KB)
- **emby-assistant-48.png** - 48x48 px (4.4 KB)
- **emby-assistant-32.png** - 32x32 px (2.3 KB)

## Usage

### Desktop Entry
The `emby-monitor.desktop` file uses the rounded icon:
```
Icon=/path/to/emby-helper/icon/emby-assistant-rounded.png
```

### GTK Application
The GTK application can set the window icon in `app_gtk.py`:
```python
self.set_icon_from_file("icon/emby-assistant-rounded.png")
```

### System Installation
To install icons system-wide on Linux:

```bash
# Copy to local icons directory
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp emby-assistant-256.png ~/.local/share/icons/hicolor/256x256/apps/emby-assistant.png

mkdir -p ~/.local/share/icons/hicolor/128x128/apps
cp emby-assistant-128.png ~/.local/share/icons/hicolor/128x128/apps/emby-assistant.png

mkdir -p ~/.local/share/icons/hicolor/64x64/apps
cp emby-assistant-64.png ~/.local/share/icons/hicolor/64x64/apps/emby-assistant.png

mkdir -p ~/.local/share/icons/hicolor/48x48/apps
cp emby-assistant-48.png ~/.local/share/icons/hicolor/48x48/apps/emby-assistant.png

mkdir -p ~/.local/share/icons/hicolor/32x32/apps
cp emby-assistant-32.png ~/.local/share/icons/hicolor/32x32/apps/emby-assistant.png

# Update icon cache
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

Then update the desktop entry to use:
```
Icon=emby-assistant
```

## Regenerating Sizes

To regenerate icon sizes from the original:

```bash
cd icon/
convert emby-assistant-rounded.png -resize 256x256 emby-assistant-256.png
convert emby-assistant-rounded.png -resize 128x128 emby-assistant-128.png
convert emby-assistant-rounded.png -resize 64x64 emby-assistant-64.png
convert emby-assistant-rounded.png -resize 48x48 emby-assistant-48.png
convert emby-assistant-rounded.png -resize 32x32 emby-assistant-32.png
```

Requires ImageMagick: `sudo apt-get install imagemagick`

## Icon Design

The icons feature:
- Media/film strip design representing Emby media server
- Purple gradient matching the app's color scheme (#667eea to #764ba2)
- Play button symbolizing media playback
- Activity indicator dots showing monitoring functionality

## License

Icons are part of the Emby Helper project and follow the same MIT License.
