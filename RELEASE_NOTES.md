# Release Notes - v1.0.0

We are excited to announce the release of **Emby Assistant v1.0.0**! This major update brings significant improvements to the browsing experience, performance optimizations for the desktop application, and powerful new features for exploring your media library.

## 🌟 New Features

### 🎬 Unified Media Browser

The "Movies" tab has been completely refactored into a comprehensive **Media Browser**:

- **All Libraries Supported**: You can now browse Movies, TV Shows, Music, and Collections from a single interface.
- **Smart Filtering**: The application intelligently filters content based on your selection:
  - **"All Libraries"**: Focuses on major video content (Movies, Series) to keep your view clean.
  - **Specific Libraries**: Automatically unlocks full content types (e.g., Music Albums for Music libraries, Episodes for TV).
- **Seamless Navigation**: Switch between libraries instantly without losing context.

### 👥 Cast & Crew Explorer

New dedicated **Cast Explorer** tab (GTK) and page (Web):

- **Search & Browse**: Easily find actors, directors, and other crew members.
- **Rich Profiles**: View detailed biographies, birth information, and oversized headshots.
- **Filmography**: See a "Appears In" carousel showing all movies and series associated with the person.

### ⚡ Performance & Responsiveness

(GTK Desktop Application)

- **Multi-threaded Loading**: All heavy data operations (library fetching, movie loading, task updates) now run in background threads.
- **Fluid UI**: The interface remains fully responsive even while loading large libraries.
- **Visual Feedback**: New pulsing progress bars indicate activity without locking the window.

## 🎨 UI Enhancements

- **Refined Layouts**: Cleaner card designs, better spacing, and improved typography.
- **High-Quality Images**: Increased resolution for movie posters and actor images (up to 450px height) with proper aspect ratio preservation.
- **Modern Badges**: Color-coded badges for different media types and task statuses.
- **Deprecation Fixes**: Updated codebase to use modern GTK/Pango markup, resolving legacy warnings.

## 🛠 Fixes

- **Mixed Content**: Resolved issues where Music albums would appear mixed with Movies.
- **Search Logic**: Improved search filtering to respect library boundaries.
- **Stability**: Fixed various potential freeze points during network requests.

---
**Upgrade Instructions:**
Simply pull the latest changes and run your preferred launcher:

- Web: `./start.sh`
- Desktop: `./start_gtk.sh`
