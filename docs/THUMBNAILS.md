# Thumbnail Feature Update

## What's New

Both Web and GTK versions now display **thumbnails** for movies and videos in the indexed media section!

## Features

### GTK Desktop Version
- **Automatic thumbnail loading**: When viewing indexed media, movies and videos show their poster images
- **Async loading**: Images load in the background without blocking the UI
- **Fallback icon**: Shows a generic video icon while loading or if image unavailable
- **Proper scaling**: Maintains aspect ratio, max 100x150px
- **Performance**: Threaded image downloading for smooth experience

### Web Version
- **Inline thumbnails**: Movie and video items show poster images on the left
- **Responsive layout**: Flexbox layout adjusts to content
- **Error handling**: Falls back to film emoji (🎬) if image fails to load
- **Lazy loading**: Images load as they're rendered
- **Clean design**: Rounded corners, proper spacing

## How It Works

### Image Source
- Thumbnails are fetched from Emby's image API
- URL: `/emby/Items/{ItemId}/Images/Primary`
- Optimized: Max 150px height, 100px width, 90% quality

### GTK Implementation
```python
# In app_gtk.py
- GdkPixbuf used for image handling
- Threading for async downloads
- GLib.idle_add for thread-safe UI updates
```

### Web Implementation
```html
<!-- In templates/index.html -->
<div class="media-item">
    <div class="thumbnail">
        <img src="/api/image/{item_id}" onerror="this.parentElement.innerHTML='🎬'">
    </div>
    <div class="content">
        <!-- Item details -->
    </div>
</div>
```

## Media Types with Thumbnails

✅ **Movies** - Show poster/primary image  
✅ **Videos** - Show thumbnail if available  
❌ **Episodes** - No thumbnail (to save space and reduce API calls)  
❌ **Series** - No thumbnail (shows series info instead)

## Visual Layout

### Before
```
[Badge] Movie Name
📅 Added: 2025-12-22
📁 /path/to/file.mkv
```

### After
```
┌──────────┐  [Badge] Movie Name
│          │  📅 Added: 2025-12-22
│  Poster  │  📁 /path/to/file.mkv
│          │
└──────────┘
```

## Performance Impact

### GTK Version
- **Memory**: +5-10 MB for cached thumbnails
- **Network**: One request per movie/video (cached by Emby)
- **CPU**: Minimal (handled in background threads)

### Web Version
- **Browser cache**: Images cached automatically
- **Network**: Same as GTK
- **Rendering**: No noticeable impact

## Configuration

No additional configuration needed! Works automatically if:
- Emby server has media with images
- API key has permission to access images
- Network connectivity to Emby server

## Troubleshooting

### Thumbnails Not Showing

**GTK Version:**
1. Check terminal for error messages
2. Verify `requests` library is installed: `pip install requests`
3. Test image URL manually:
   ```bash
   curl -H "X-Emby-Token: YOUR_KEY" \
     "http://your-server:8096/emby/Items/ITEM_ID/Images/Primary"
   ```

**Web Version:**
1. Open browser console (F12) for errors
2. Check `/api/image/{id}` endpoint responds
3. Verify image proxy route in `app.py`

### Slow Loading

- **Normal behavior**: Images load asynchronously
- **Emby server load**: Many concurrent requests may slow Emby
- **Network speed**: Slow connection = slower images
- **Solution**: Images are cached after first load

## Technical Details

### GTK Image Loading Pipeline
```
Emby API → requests.get() → BytesIO → GdkPixbuf.PixbufLoader 
  → scale_simple() → GLib.idle_add() → Gtk.Image.set_from_pixbuf()
```

### Web Image Loading
```
Browser → /api/image/{id} → Flask proxy → Emby API 
  → Response with image bytes → Browser renders
```

## Future Enhancements

Possible improvements:
- [ ] Disk cache for thumbnails (reduce API calls)
- [ ] Thumbnail for TV episodes
- [ ] Larger preview on hover
- [ ] Background/backdrop images
- [ ] Thumbnail grid view option
- [ ] Custom thumbnail size setting

## Code Files Modified

- `app_gtk.py` - Added thumbnail loading and display
- `app.py` - Added image proxy endpoint
- `templates/index.html` - Updated CSS and JS for thumbnails

## Compatibility

- ✅ Emby Server 4.x and later
- ✅ All media with Primary image type
- ✅ Works with existing configurations
- ✅ No breaking changes

Enjoy your visual media library! 🎬📺
