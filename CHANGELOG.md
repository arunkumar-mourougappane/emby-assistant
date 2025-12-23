# Changelog

## [v1.0.0] - 2025-12-22

- **Cast & Crew Explorer**: Dedicated page (`/cast`) for browsing people
  - Search functionality to find actors/directors by name
  - Detailed Person Modal:
    - Displays Biography, Birth Date, and Place of Birth
    - "Appears In" horizontal carousel of movie credits
  - Infinite scrolling support for cast lists
  - **GTK Support**: Full feature parity in `app_gtk.py` with Grid layout and native dialogs

- **Server Status Enhancements**:
  - Live Server Clock on Dashboard (updates every second)
  - Improved dark mode support for status cards
  - **GTK Support**: Clock added to server info header

### Fixed

- **"Open in Emby" Link**:
  - Fixed erroneous `localhost` URL generation
  - Now uses correct configured Server URL
  - Correctly maps `serverId` to the actual Emby System ID instead of Movie ID

- **Layout Issues**:
  - Fixed aspect ratio for person images
  - Resolved infinite scroll jitter in media libraries

### Added

- **Library-Based Movies Organization**: Movies now organized by Emby library structure
  - New `/api/libraries` endpoint for fetching available movie libraries
  - Library tabs in Web UI to filter movies by library
  - Library dropdown in GTK app for filtering movies
  - Support for displaying all movies or filtering by specific library
  - Automatic library detection and tab/dropdown population
  - Improved movie limit from 50 to 200 for better browsing

- **Movies Browser**: Comprehensive movie browsing and detailed information viewer
  - Updated `/api/movies` endpoint now supports optional `libraryId` parameter for filtering
  - New `/api/item/<item_id>` endpoint for detailed item information
  - Horizontal scrolling movie poster carousel in Web UI (200 movies per library)
  - Grid layout movie browser in GTK app with FlowBox
  - Clickable movie cards that open detailed information modal/dialog
  - Movie details include: poster, title, year, genres, rating, runtime, overview, file info, and cast
  - Horizontal scrolling cast carousel with actor photos and roles
  - "Open in Emby" button that links directly to the movie in Emby web interface
  - Fallback to file information when metadata is missing
  - Works seamlessly in both Web UI and GTK desktop app

- **Person/Cast Support**: Added support for displaying cast and crew (Person type) with profile images
  - Person images display as circular thumbnails (150x150)
  - New `/api/person-image/<person_id>` endpoint for fetching person headshots
  - Cyan-colored badge for Person type items
  - Support in both Web UI and GTK desktop app

- **Thumbnail Fallback**: Intelligent image fallback system
  - When Primary cover image is not available, automatically tries Thumb image
  - Applies to all media types (Movies, Videos, Persons)
  - Works in both Web UI and GTK app
  - Seamless user experience with no broken images

- **Detailed Server Information**: Comprehensive server details view
  - New `/api/server-details` endpoint for detailed server data
  - Modal dialog in Web UI showing system, network, paths, and capabilities
  - GTK dialog with organized sections for all server information
  - Displays: Product info, version, OS, architecture, runtime, network addresses, ports, file paths, and server capabilities
  - Easy access via "Server Details" button in header

### Changed

- **Higher Quality Images with No Distortion**: Significant improvement to image loading and display
  - Web UI: Movie posters now use `maxHeight: 450px` and `quality: 95` (up from 150px/90)
  - Web UI: Person images now use `maxHeight: 200px` and `quality: 95` (up from 150px/90)
  - GTK App: Movie posters now use `maxHeight: 450px` and `quality: 95` (up from 150px/90)
  - GTK App: Person images now use `maxHeight: 200px` and `quality: 95` (up from 150px/90)
  - Removed `maxWidth` constraint to preserve aspect ratio and prevent distortion
  - Web UI: Changed `object-fit: cover` to `object-fit: contain` for proper aspect ratio
  - Images now fetch at higher resolution when available
  - No more stretched or squished images - all images maintain natural proportions

- **Web UI - Bootstrap Migration**: Complete redesign using Bootstrap 5.3.2 and jQuery 3.7.1
  - All assets hosted locally in `static/` directory (no CDN dependencies)
  - Modern, responsive card-based layout
  - Improved visual hierarchy with gradient backgrounds
  - Enhanced loading states with Bootstrap spinners
  - Better mobile responsiveness with Bootstrap grid system
  - Cleaner alert/error messaging
  - Improved accessibility with ARIA labels

- **GTK App - Image Aspect Ratio Fix**:
  - Images now maintain their natural aspect ratio (no distortion)
  - Proper scaling algorithm that fits images within max dimensions
  - Separate handling for portrait posters and person images
  - Higher resolution image loading for better quality
  - Images centered within their container boxes

### Fixed

- **Error Handling**: Improved error handling for missing/deleted items
  - 404 errors for missing items are now handled silently without console spam
  - Better error messages when movie details cannot be loaded
  - Graceful fallback when items referenced in lists have been deleted from server

### Technical Details

#### Web UI Files

- `templates/index.html`: Complete Bootstrap redesign + Movies browser with carousel
- `static/css/bootstrap.min.css`: Bootstrap 5.3.2 CSS (228KB)
- `static/js/bootstrap.bundle.min.js`: Bootstrap 5.3.2 JS bundle (80KB)
- `static/js/jquery.min.js`: jQuery 3.7.1 (88KB)

#### Backend Changes

- `emby_client.py`:
  - Added `get_libraries()` method for fetching media libraries
  - Added `get_movies_by_library()` method for fetching movies with optional library filtering
  - Existing `get_movies()` method retained for backward compatibility
  - Added `get_item_details()` method for detailed item information
- `app.py`:
  - Added `/api/libraries` endpoint for fetching available movie libraries
  - Updated `/api/movies` endpoint with new `libraryId` query parameter for filtering
  - Updated `/api/image/<item_id>` endpoint to use higher quality (maxHeight: 450, quality: 95)
  - Updated `/api/person-image/<person_id>` endpoint to use higher quality (maxHeight: 200, quality: 95)
  - Added `/api/item/<item_id>` endpoint for detailed item info
  - Movie endpoint includes: genres, cast, runtime, ratings, file paths, media streams, parent_id
- `app_gtk.py`:
  - Added `create_movies_tab()` with library dropdown selector for filtering
  - Added `load_libraries()` method to populate library dropdown
  - Updated `load_movies()` to support library filtering based on dropdown selection
  - Added `create_movie_card()` for clickable movie cards
  - Added `show_movie_details()` dialog with poster, metadata, cast carousel, and Emby link
  - Updated `load_thumbnail()` with higher quality settings and aspect ratio preservation
  - Modified `create_media_row()` to handle Person type
  - Added Person badge color (#06b6d4)

#### Image Handling

- **Movies/Videos**: Up to 450px height, quality 95 (Web UI and GTK)
- **Persons**: Up to 200px height, quality 95 (Web UI and GTK)
- No width constraint - aspect ratio preserved automatically
- Images scale intelligently to fit within max dimensions
- Web UI uses `object-fit: contain` for proper aspect ratio
- GTK app uses mathematical scaling with BILINEAR interpolation
- Fallback icons: 🎬 for media, 👤 for persons

### Dependencies

No new Python dependencies required. Static assets are self-contained.

### Browser Compatibility

Bootstrap 5.3.2 supports:

- Chrome, Firefox, Safari, Edge (latest versions)
- iOS Safari 12+
- Android Chrome

### Migration Notes

- Old web UI completely replaced with Bootstrap version
- No breaking changes to API endpoints
- GTK app maintains same functionality with improved visuals
