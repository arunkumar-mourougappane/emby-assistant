#!/usr/bin/env python3
"""GTK Desktop Application for Emby Assistant."""

# Standard library imports
import threading
from datetime import datetime

# Third-party imports
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("GdkPixbuf", "2.0")
# noqa: E402 - gi.require_version must be called before importing from gi
from gi.repository import GdkPixbuf, GLib, Gtk, Pango  # noqa: E402

import requests  # noqa: E402

# Local imports
import config  # noqa: E402
from emby_client import EmbyClient  # noqa: E402


class EmbyMonitorApp(Gtk.Window):
    """Main GTK application window for Emby monitoring."""

    def __init__(self):
        """Initialize the GTK application."""
        super().__init__(title="Emby Assistant")

        # Initialize Emby client
        try:
            config.validate_config()
            self.emby = EmbyClient(config.EMBY_SERVER_URL, config.EMBY_API_KEY)
        except ValueError as e:
            self.show_error_dialog(f"Configuration Error: {e}")
            exit(1)

        # Set window icon
        try:
            import os

            icon_path = os.path.join(
                os.path.dirname(__file__), "icon", "emby-assistant-128.png"
            )
            if os.path.exists(icon_path):
                self.set_icon_from_file(icon_path)
        except Exception:
            # Icon loading is non-critical
            pass

        # Window settings
        self.set_default_size(1200, 800)
        self.set_border_width(10)

        # Create main layout
        self.create_ui()

        # Start auto-refresh timers
        self.start_refresh_timers()

        # Initial data load
        self.refresh_all()

    def create_ui(self):
        """Create the user interface."""
        # Initialize progress bar early so it's available for load_* calls
        self.main_progress_bar = Gtk.ProgressBar()
        self.main_progress_bar.set_pulse_step(0.1)
        self.main_progress_bar.set_no_show_all(True) # Hidden by default
        self.main_progress_bar.hide()

        # Main vertical box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_vbox)

        # Header section
        header_frame = self.create_header()
        main_vbox.pack_start(header_frame, False, False, 0)

        # Notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_vbox.pack_start(notebook, True, True, 0)

        # Tab 1: Current Processing
        processing_box = self.create_processing_tab()
        notebook.append_page(
            processing_box, Gtk.Label(label="🔄 Current Processing")
        )

        # Tab 2: Completed Tasks
        completed_box = self.create_completed_tab()
        notebook.append_page(
            completed_box, Gtk.Label(label="✅ Completed Tasks")
        )

        # Tab 3: Media Browser
        movies_box = self.create_movies_tab()
        notebook.append_page(movies_box, Gtk.Label(label="🎬 Media"))

        # Tab 4: Cast Explorer
        cast_box = self.create_cast_tab()
        notebook.append_page(cast_box, Gtk.Label(label="👥 Cast"))

        # Tab 5: Indexed Media
        media_box = self.create_media_tab()
        notebook.append_page(media_box, Gtk.Label(label="📁 Indexed Media"))

        # Tab 6: All Tasks
        tasks_box = self.create_all_tasks_tab()
        notebook.append_page(tasks_box, Gtk.Label(label="📋 All Tasks"))

        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context = self.statusbar.get_context_id("main")
        
        main_vbox.pack_start(self.main_progress_bar, False, False, 0)
        main_vbox.pack_start(self.statusbar, False, False, 0)

    def show_progress(self):
        """Show main progress bar."""
        self.main_progress_bar.show()
        self.main_progress_timer = GLib.timeout_add(100, self._pulse_progress)

    def hide_progress(self):
        """Hide main progress bar."""
        self.main_progress_bar.hide()
        if hasattr(self, 'main_progress_timer') and self.main_progress_timer:
             GLib.source_remove(self.main_progress_timer)
             self.main_progress_timer = None

    def _pulse_progress(self):
        """Pulse the progress bar."""
        self.main_progress_bar.pulse()
        return True

    def create_header(self):
        """Create header with server information."""
        frame = Gtk.Frame(label="Server Information")
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)
        frame.add(vbox)

        # Server status row
        status_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=10
        )
        self.status_indicator = Gtk.Label()
        self.status_indicator.set_markup("<span size='large'>⚫</span>")
        status_box.pack_start(self.status_indicator, False, False, 0)

        self.server_name_label = Gtk.Label(label="Loading...")
        self.server_name_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.server_name_label, False, False, 0)

        vbox.pack_start(status_box, False, False, 0)

        # Server info row
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.version_label = Gtk.Label(label="Version: -")
        self.version_label.set_halign(Gtk.Align.START)
        info_box.pack_start(self.version_label, False, False, 0)

        self.os_label = Gtk.Label(label="OS: -")
        self.os_label.set_halign(Gtk.Align.START)
        info_box.pack_start(self.os_label, False, False, 0)

        self.url_label = Gtk.Label()
        self.url_label.set_markup(
            f"<small>URL: {config.EMBY_SERVER_URL}</small>"
        )
        self.url_label.set_halign(Gtk.Align.START)
        info_box.pack_start(self.url_label, False, False, 0)

        # Time label
        self.time_label = Gtk.Label()
        self.time_label.set_markup("<small>🕒 --:--:--</small>")
        self.time_label.set_halign(Gtk.Align.END)
        
        # Spacer to push time to the right
        spacer = Gtk.Label()
        info_box.pack_start(spacer, True, True, 0)
        info_box.pack_start(self.time_label, False, False, 0)

        vbox.pack_start(info_box, False, False, 0)

        # Button box
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        refresh_btn = Gtk.Button(label="🔄 Refresh All")
        refresh_btn.connect("clicked", lambda w: self.refresh_all())
        btn_box.pack_start(refresh_btn, False, False, 0)

        details_btn = Gtk.Button(label="ℹ️ Server Details")
        details_btn.connect("clicked", lambda w: self.show_server_details())
        btn_box.pack_start(details_btn, False, False, 0)

        vbox.pack_start(btn_box, False, False, 5)

        return frame

    def create_processing_tab(self):
        """Create the current processing tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        # Scrolled window for processing items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.processing_listbox = Gtk.ListBox()
        self.processing_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.processing_listbox)

        vbox.pack_start(scrolled, True, True, 0)

        # Auto-refresh label
        auto_label = Gtk.Label()
        auto_label.set_markup(
            "<small><i>Auto-refreshes every 5 seconds</i></small>"
        )
        auto_label.set_halign(Gtk.Align.END)
        vbox.pack_start(auto_label, False, False, 0)

        return vbox

    def create_completed_tab(self):
        """Create the completed tasks tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.completed_listbox = Gtk.ListBox()
        self.completed_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.completed_listbox)

        vbox.pack_start(scrolled, True, True, 0)

        return vbox

    def create_media_tab(self):
        """Create the indexed media tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        # Limit selector
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.pack_start(Gtk.Label(label="Show:"), False, False, 0)

        self.media_limit_combo = Gtk.ComboBoxText()
        self.media_limit_combo.append_text("50 items")
        self.media_limit_combo.append_text("100 items")
        self.media_limit_combo.append_text("200 items")
        self.media_limit_combo.set_active(0)
        self.media_limit_combo.connect(
            "changed", lambda w: self.load_indexed_media()
        )
        hbox.pack_start(self.media_limit_combo, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)

        # Scrolled window for media items
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.media_listbox = Gtk.ListBox()
        self.media_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.media_listbox)

        vbox.pack_start(scrolled, True, True, 0)

        return vbox


    def create_all_tasks_tab(self):
        """Create the all tasks tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.tasks_listbox = Gtk.ListBox()
        self.tasks_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.tasks_listbox)

        vbox.pack_start(scrolled, True, True, 0)

        return vbox

    def create_processing_row(self, item):
        """Create a row for a processing item."""
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        badge = Gtk.Label()
        badge.set_markup(
            f"<span background='#10b981' foreground='white' "
            f"size='small'> {item['state']} </span>"
        )
        title_box.pack_start(badge, False, False, 0)

        title = Gtk.Label(label=item["task_name"])
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title.modify_font(Pango.FontDescription("bold 11"))
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Category and description
        if item.get("category"):
            cat_label = Gtk.Label()
            cat_label.set_markup(
                f"<small>Category: {item['category']}</small>"
            )
            cat_label.set_halign(Gtk.Align.START)
            vbox.pack_start(cat_label, False, False, 0)

        if item.get("description"):
            desc_label = Gtk.Label(label=item["description"])
            desc_label.set_halign(Gtk.Align.START)
            desc_label.set_line_wrap(True)
            desc_label.modify_font(Pango.FontDescription("9"))
            vbox.pack_start(desc_label, False, False, 0)

        # Progress bar
        progress = Gtk.ProgressBar()
        progress.set_fraction(item["progress"] / 100.0)
        progress.set_text(f"{item['progress']:.1f}%")
        progress.set_show_text(True)
        vbox.pack_start(progress, False, False, 0)

        # Time
        if item.get("started_at"):
            time_label = Gtk.Label()
            time_label.set_markup(
                f"<small>Started: {item['started_at']}</small>"
            )
            time_label.set_halign(Gtk.Align.START)
            vbox.pack_start(time_label, False, False, 0)

        row.add(vbox)
        return row

    def create_completed_row(self, task):
        """Create a row for a completed task."""
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)

        # Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        badge = Gtk.Label()
        badge.set_markup(
            "<span background='#3b82f6' foreground='white' "
            "size='small'> ✓ Completed </span>"
        )
        title_box.pack_start(badge, False, False, 0)

        title = Gtk.Label()
        title.set_markup(f"<span weight='bold' size='11000'>{GLib.markup_escape_text(task['name'])}</span>")
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Details
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)

        cat_label = Gtk.Label()
        cat_label.set_markup(f"<small>Category: {GLib.markup_escape_text(task['category'])}</small>")
        info_box.pack_start(cat_label, False, False, 0)

        dur_label = Gtk.Label()
        dur_label.set_markup(f"<small>⏱️ Duration: {task['duration']}</small>")
        info_box.pack_start(dur_label, False, False, 0)

        info_box.set_halign(Gtk.Align.START)
        vbox.pack_start(info_box, False, False, 0)

        # Time
        time_label = Gtk.Label()
        time_label.set_markup(
            f"<small>Completed: {task['completed_at']}</small>"
        )
        time_label.set_halign(Gtk.Align.START)
        vbox.pack_start(time_label, False, False, 0)

        row.add(vbox)
        return row

    def create_movie_card(self, movie):
        """Create a movie card for the grid layout."""
        # Event box to make the entire card clickable
        event_box = Gtk.EventBox()
        event_box.connect("button-press-event", lambda w, e: self.show_movie_details(movie))

        # Main vertical box for movie card
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)

        # Poster image container
        poster_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        poster_box.set_size_request(200, 300)
        poster_box.set_halign(Gtk.Align.CENTER)
        poster_box.set_valign(Gtk.Align.CENTER)

        poster_image = Gtk.Image()
        poster_image.set_from_icon_name("video-x-generic", Gtk.IconSize.DIALOG)
        poster_box.pack_start(poster_image, True, False, 0)
        vbox.pack_start(poster_box, False, False, 0)

        # Load poster asynchronously
        if movie.get("Id"):
            threading.Thread(
                target=self.load_thumbnail,
                args=(movie["Id"], poster_image, False),
                daemon=True,
            ).start()

        # Movie title
        title_text = GLib.markup_escape_text(movie.get("Name", "Unknown"))
        title_label = Gtk.Label()
        title_label.set_markup(f"<span font='bold 10'>{title_text}</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        title_label.set_line_wrap(True)
        title_label.set_max_width_chars(20)
        vbox.pack_start(title_label, False, False, 0)

        # Year
        if movie.get("ProductionYear"):
            year_label = Gtk.Label()
            year_label.set_markup(f"<span font='9'>{movie['ProductionYear']}</span>")
            year_label.set_halign(Gtk.Align.CENTER)
            vbox.pack_start(year_label, False, False, 0)

        # Rating
        if movie.get("CommunityRating"):
            rating_label = Gtk.Label()
            rating_label.set_markup(
                f"<small>⭐ {movie['CommunityRating']:.1f}</small>"
            )
            rating_label.set_halign(Gtk.Align.CENTER)
            vbox.pack_start(rating_label, False, False, 0)

        event_box.add(vbox)
        return event_box

    def create_media_row(self, item):
        """Create a row for a media item."""
        row = Gtk.ListBoxRow()

        # Main horizontal box to hold thumbnail and content
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_hbox.set_border_width(10)

        # Thumbnail placeholder (will be loaded asynchronously)
        if item["type"] in ["Movie", "Video"] and item.get("id"):
            # Create a box to hold the image with fixed dimensions
            thumbnail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            thumbnail_box.set_size_request(100, 150)
            thumbnail_box.set_halign(Gtk.Align.CENTER)
            thumbnail_box.set_valign(Gtk.Align.CENTER)

            thumbnail_image = Gtk.Image()
            thumbnail_image.set_from_icon_name(
                "video-x-generic", Gtk.IconSize.DIALOG
            )
            thumbnail_box.pack_start(thumbnail_image, True, False, 0)
            main_hbox.pack_start(thumbnail_box, False, False, 0)

            # Load thumbnail asynchronously
            threading.Thread(
                target=self.load_thumbnail,
                args=(item["id"], thumbnail_image, False),
                daemon=True,
            ).start()
        elif item["type"] == "Person" and item.get("id"):
            # Create a box to hold the image with fixed dimensions
            thumbnail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            thumbnail_box.set_size_request(150, 150)
            thumbnail_box.set_halign(Gtk.Align.CENTER)
            thumbnail_box.set_valign(Gtk.Align.CENTER)

            thumbnail_image = Gtk.Image()
            thumbnail_image.set_from_icon_name(
                "avatar-default", Gtk.IconSize.DIALOG
            )
            thumbnail_box.pack_start(thumbnail_image, True, False, 0)
            main_hbox.pack_start(thumbnail_box, False, False, 0)

            # Load person thumbnail asynchronously
            threading.Thread(
                target=self.load_thumbnail,
                args=(item["id"], thumbnail_image, True),
                daemon=True,
            ).start()

        # Content vbox (text information)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Title with type badge
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Badge color based on type
        badge_colors = {
            "Episode": "#8b5cf6",
            "Movie": "#f59e0b",
            "Series": "#ec4899",
            "Person": "#06b6d4",
        }
        color = badge_colors.get(item["type"], "#6b7280")

        badge = Gtk.Label()
        badge.set_markup(
            f"<span background='{color}' foreground='white' "
            f"size='small'> {item['type']} </span>"
        )
        title_box.pack_start(badge, False, False, 0)

        # Format display name
        display_name = item["name"]
        if item["type"] == "Episode" and item.get("series_name"):
            display_name = (
                f"{item['series_name']} - "
                f"S{item.get('season', '?')}E{item.get('episode', '?')} - "
                f"{item['name']}"
            )

        title = Gtk.Label()
        title.set_markup(f"<span weight='bold' size='10240'>{GLib.markup_escape_text(display_name)}</span>")
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Added date
        date_label = Gtk.Label()
        date_label.set_markup(f"<small>📅 Added: {item['added_at']}</small>")
        date_label.set_halign(Gtk.Align.START)
        vbox.pack_start(date_label, False, False, 0)

        # Path
        if item.get("path"):
            path_label = Gtk.Label()
            path_label.set_markup(f"<small>📁 {item['path']}</small>")
            path_label.set_halign(Gtk.Align.START)
            path_label.set_line_wrap(True)
            path_label.set_max_width_chars(100)
            path_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            vbox.pack_start(path_label, False, False, 0)

        main_hbox.pack_start(vbox, True, True, 0)
        row.add(main_hbox)
        return row

    def create_task_row(self, task):
        """Create a row for a task."""
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)

        # Title with state
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        state_colors = {
            "Running": "#10b981",
            "Idle": "#6b7280",
            "Cancelling": "#ef4444",
        }
        color = state_colors.get(task["state"], "#6b7280")

        badge = Gtk.Label()
        badge.set_markup(
            f"<span background='{color}' foreground='white' "
            f"size='small'> {task['state']} </span>"
        )
        title_box.pack_start(badge, False, False, 0)

        title = Gtk.Label()
        title.set_markup(f"<span weight='bold' size='10240'>{GLib.markup_escape_text(task['name'])}</span>")
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Category
        cat_label = Gtk.Label()
        cat_label.set_markup(f"<small>Category: {GLib.markup_escape_text(task['category'])}</small>")
        cat_label.set_halign(Gtk.Align.START)
        vbox.pack_start(cat_label, False, False, 0)

        # Progress if running
        if task["state"] == "Running" and task["current_progress"] > 0:
            progress = Gtk.ProgressBar()
            progress.set_fraction(task["current_progress"] / 100.0)
            progress.set_text(f"{task['current_progress']:.1f}%")
            progress.set_show_text(True)
            vbox.pack_start(progress, False, False, 0)

        # Last execution
        if task.get("last_end") and task["last_end"] != "N/A":
            exec_label = Gtk.Label()
            exec_label.set_markup(
                f"<small>Last completed: {task['last_end']} "
                f"({task['last_status']})</small>"
            )
            exec_label.set_halign(Gtk.Align.START)
            vbox.pack_start(exec_label, False, False, 0)

        row.add(vbox)
        return row

    def load_thumbnail(self, item_id, image_widget, is_person=False):
        """Load thumbnail image for a media item asynchronously with fallback."""
        try:
            # Set dimensions based on type - use higher quality
            if is_person:
                max_width = 200
                max_height = 200
            else:
                max_width = 300
                max_height = 450

            # Only set maxHeight to preserve aspect ratio, use higher quality
            params = f"maxHeight={max_height}&quality=95"

            # Try Primary image first
            image_url = (
                f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/"
                f"Images/Primary?{params}"
            )
            response = requests.get(
                image_url,
                headers={"X-Emby-Token": config.EMBY_API_KEY},
                timeout=5
            )

            # If Primary not found, try Thumb as fallback
            if response.status_code == 404:
                image_url = (
                    f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/"
                    f"Images/Thumb?{params}"
                )
                response = requests.get(
                    image_url,
                    headers={"X-Emby-Token": config.EMBY_API_KEY},
                    timeout=5
                )

            if response.status_code == 200:
                # Load image from bytes
                loader = GdkPixbuf.PixbufLoader()
                loader.write(response.content)
                loader.close()
                pixbuf = loader.get_pixbuf()

                # Scale image while maintaining aspect ratio
                if pixbuf:
                    orig_width = pixbuf.get_width()
                    orig_height = pixbuf.get_height()

                    # Calculate scaling factor to fit within max dimensions
                    # while maintaining aspect ratio
                    width_ratio = max_width / orig_width
                    height_ratio = max_height / orig_height
                    scale_ratio = min(width_ratio, height_ratio)

                    # Calculate new dimensions
                    new_width = int(orig_width * scale_ratio)
                    new_height = int(orig_height * scale_ratio)

                    # Scale the pixbuf
                    scaled_pixbuf = pixbuf.scale_simple(
                        new_width, new_height, GdkPixbuf.InterpType.BILINEAR
                    )

                    # Update image widget on main thread
                    GLib.idle_add(image_widget.set_from_pixbuf, scaled_pixbuf)
        except Exception:
            # If image load fails, keep the default icon
            pass

    def format_datetime(self, dt_str):
        """Format datetime string."""
        if not dt_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            return dt_str

    def calculate_duration(self, start_str, end_str):
        """Calculate duration."""
        if not start_str or not end_str:
            return "N/A"
        try:
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            duration = end - start

            seconds = int(duration.total_seconds())
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                return f"{seconds // 60}m {seconds % 60}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        except (ValueError, AttributeError):
            return "N/A"

    def load_server_status(self):
        """Load server status information."""

    def load_server_status(self):
        """Load server status information."""
        def worker():
             try:
                 system_info = self.emby.get_system_info()
                 GLib.idle_add(on_worker_done, system_info)
             except Exception:
                 GLib.idle_add(on_worker_done, None)

        def on_worker_done(system_info):
            if not system_info:
                if hasattr(self, 'status_indicator'):
                    self.status_indicator.set_markup(
                        "<span size='large' foreground='red'>⚫</span>"
                    )
                if hasattr(self, 'server_name_label'):
                    self.server_name_label.set_markup(
                        "<span foreground='red'>Could not connect to server</span>"
                    )
                return False

            if hasattr(self, 'status_indicator'):
                self.status_indicator.set_markup(
                    "<span size='large' foreground='green'>🟢</span>"
                )
            if hasattr(self, 'server_name_label'):
                self.server_name_label.set_markup(
                    f"<b>{system_info.get('ServerName', 'Unknown')}</b>"
                )
            if hasattr(self, 'version_label'):
                self.version_label.set_text(
                    f"Version: {system_info.get('Version', 'Unknown')}"
                )
            if hasattr(self, 'os_label'):
                self.os_label.set_text(
                    f"OS: {system_info.get('OperatingSystem', 'Unknown')}"
                )

            self.update_statusbar("Server status updated")
            return False

        threading.Thread(target=worker, daemon=True).start()

    def load_current_processing(self):
        """Load currently processing media."""

    def load_current_processing(self):
        """Load currently processing media."""
        def worker():
            try:
                processing = self.emby.get_processing_media()
                GLib.idle_add(on_worker_done, processing)
            except Exception as e:
                print(f"Error loading processing: {e}")

        def on_worker_done(processing):
            # Clear existing items
            for child in self.processing_listbox.get_children():
                self.processing_listbox.remove(child)

            if not processing:
                label = Gtk.Label(label="✨ No active processing tasks")
                label.set_margin_top(50)
                label.set_margin_bottom(50)
                self.processing_listbox.add(label)
            else:
                for item in processing:
                    formatted_item = {
                        "task_name": item.get("task_name", "Unknown"),
                        "state": item.get("state", "Unknown"),
                        "progress": round(item.get("progress", 0), 1),
                        "category": item.get("category", "Unknown"),
                        "description": item.get("description", ""),
                        "started_at": self.format_datetime(
                            item.get("last_execution_time", "")
                        ),
                    }
                    self.processing_listbox.add(
                        self.create_processing_row(formatted_item)
                    )

            self.processing_listbox.show_all()
            return False

        threading.Thread(target=worker, daemon=True).start()

    def load_completed_tasks(self):
        """Load recently completed tasks."""

    def load_completed_tasks(self):
        """Load recently completed tasks."""
        def worker():
            try:
                completed = self.emby.get_completed_tasks(limit=15)
                GLib.idle_add(on_worker_done, completed)
            except Exception as e:
                 print(f"Error loading completed tasks: {e}")

        def on_worker_done(completed):
            # Clear existing items
            for child in self.completed_listbox.get_children():
                self.completed_listbox.remove(child)

            if not completed:
                label = Gtk.Label(label="📋 No completed tasks")
                label.set_margin_top(50)
                label.set_margin_bottom(50)
                self.completed_listbox.add(label)
            else:
                for task in completed:
                    formatted_task = {
                        "name": task.get("name", "Unknown"),
                        "category": task.get("category", "Unknown"),
                        "status": task.get("status", "Unknown"),
                        "completed_at": self.format_datetime(
                            task.get("end_time", "")
                        ),
                        "duration": self.calculate_duration(
                            task.get("start_time", ""),
                            task.get("end_time", "")
                        ),
                    }
                    self.completed_listbox.add(
                        self.create_completed_row(formatted_task)
                    )

            self.completed_listbox.show_all()
            return False

        threading.Thread(target=worker, daemon=True).start()

    def create_movies_tab(self):
        """Create the movies browser tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        # Controls box
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Library selector
        label = Gtk.Label(label="Library:")
        controls_box.pack_start(label, False, False, 0)

        self.library_combo = Gtk.ComboBoxText()
        self.library_combo.append("all", "All Libraries")
        self.library_combo.set_active(0)
        self.library_combo.set_active(0)
        self.library_combo.connect("changed", lambda w: self.load_movies())
        controls_box.pack_start(self.library_combo, False, False, 0)

        # Search bar
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search media...")
        search_entry.connect("search-changed", self.on_movie_search_changed)
        controls_box.pack_start(search_entry, True, True, 0)

        vbox.pack_start(controls_box, False, False, 0)

        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # FlowBox with better spacing
        self.movies_flowbox = Gtk.FlowBox()
        self.movies_flowbox.set_valign(Gtk.Align.START)
        self.movies_flowbox.set_max_children_per_line(6)
        self.movies_flowbox.set_min_children_per_line(2)
        self.movies_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.movies_flowbox.set_homogeneous(True)
        self.movies_flowbox.set_column_spacing(20)
        self.movies_flowbox.set_row_spacing(20)
        scrolled.add(self.movies_flowbox)

        vbox.pack_start(scrolled, True, True, 0)

        # Initial Load
        self.load_libraries()
        self.load_movies()

        return vbox

    def on_movie_search_changed(self, entry):
        """Handle movie search."""
        query = entry.get_text()
        self.load_movies(query)

    def load_libraries(self):
        """Load libraries into combo box."""
        def worker():
            try:
                libraries = self.emby.get_libraries()
                # Sort libraries by name
                libraries.sort(key=lambda x: x.get("Name", "").lower())
                GLib.idle_add(on_worker_done, libraries)
            except Exception as e:
                 print(f"Error loading libraries: {e}")

        def on_worker_done(libraries):
            # Store library data for type lookups
            self.library_map = {lib["ItemId"]: lib for lib in libraries}

            # preserve active selection if possible, else reset
            active_id = self.library_combo.get_active_id()
            
            self.library_combo.remove_all()
            self.library_combo.append("all", "All Libraries")
            
            for lib in libraries:
                self.library_combo.append(lib.get("ItemId"), lib.get("Name", "Unknown"))
            
            if active_id:
                self.library_combo.set_active_id(active_id)
            if not self.library_combo.get_active_id():
                self.library_combo.set_active(0)
                
            return False

        threading.Thread(target=worker, daemon=True).start()

    def load_movies(self, query=None):
        """Load movies browser."""
        self.show_progress()

        # Capture state on main thread
        library_id = self.library_combo.get_active_id()
        parent_id = None if library_id == "all" else library_id
        
        # Smart Type Filtering
        include_types = "Movie,Series,season,episode,BoxSet,MusicAlbum,Audio,Video" # Default Fallback
        
        if library_id == "all":
             # All Libraries: Content Focus
             include_types = "Movie,Series,BoxSet"
        elif hasattr(self, 'library_map') and library_id in self.library_map:
             # Specific Library: Type Focus
             lib_type = self.library_map[library_id].get("CollectionType", "").lower()
             if lib_type == "movies":
                 include_types = "Movie,BoxSet"
             elif lib_type == "tvshows":
                 include_types = "Series"
             elif lib_type == "music":
                 include_types = "MusicAlbum,Audio"
             # else keep default (mixed)

        def worker():
            try:
                # Run blocking call in background thread
                media = self.emby.get_items_by_library(
                    parent_id=parent_id, 
                    limit=200, 
                    search_term=query,
                    include_item_types=include_types
                )
                # Schedule UI update on main thread
                GLib.idle_add(on_worker_done, media)
            except Exception as e:
                print(f"Error loading movies: {e}")
                GLib.idle_add(self.hide_progress)

        def on_worker_done(media):
            # Clear existing items
            for child in self.movies_flowbox.get_children():
                self.movies_flowbox.remove(child)

            if not media:
                label = Gtk.Label(label="🎬 No media found")
                label.set_margin_top(50)
                label.set_margin_bottom(50)
                self.movies_flowbox.add(label)
            else:
                for item in media:
                    card = self.create_movie_card(item)
                    self.movies_flowbox.add(card)

            self.update_statusbar(f"Loaded {len(media)} items")
            self.hide_progress()
            self.movies_flowbox.show_all()
            return False

        threading.Thread(target=worker, daemon=True).start()

    def load_indexed_media(self):
        """Load indexed media."""
        self.show_progress()

    def load_indexed_media(self):
        """Load indexed media."""
        self.show_progress()

        # Capture state
        limit_idx = self.media_limit_combo.get_active()
        limits = {0: 50, 1: 100, 2: 200}
        limit = limits.get(limit_idx, 50)

        def worker():
            try:
                items = self.emby.get_recently_added(limit=limit)
                GLib.idle_add(on_worker_done, items)
            except Exception as e:
                print(f"Error loading indexed media: {e}")
                GLib.idle_add(self.hide_progress)

        def on_worker_done(items):
            # Clear existing items
            for child in self.media_listbox.get_children():
                self.media_listbox.remove(child)

            if not items:
                label = Gtk.Label(label="🎬 No indexed media found")
                label.set_margin_top(50)
                label.set_margin_bottom(50)
                self.media_listbox.add(label)
            else:
                for item in items:
                    formatted_item = {
                        "id": item.get("Id", ""),
                        "name": item.get("Name", "Unknown"),
                        "type": item.get("Type", "Unknown"),
                        "added_at": self.format_datetime(
                            item.get("DateCreated", "")
                        ),
                        "path": item.get("Path", "N/A"),
                        "series_name": item.get("SeriesName", ""),
                        "season": item.get("ParentIndexNumber", ""),
                        "episode": item.get("IndexNumber", ""),
                    }
                    self.media_listbox.add(
                        self.create_media_row(formatted_item)
                    )

            self.media_listbox.show_all()
            self.update_statusbar(f"Loaded {len(items)} media items")
            self.hide_progress()
            return False

        threading.Thread(target=worker, daemon=True).start()

    def load_all_tasks(self):
        """Load all scheduled tasks."""
        def worker():
             try:
                 tasks = self.emby.get_scheduled_tasks()
                 GLib.idle_add(on_worker_done, tasks)
             except Exception as e:
                 print(f"Error loading tasks: {e}")

        def on_worker_done(tasks):
            # Clear existing items
            for child in self.tasks_listbox.get_children():
                self.tasks_listbox.remove(child)

            if not tasks:
                label = Gtk.Label(label="📋 No tasks found")
                label.set_margin_top(50)
                label.set_margin_bottom(50)
                self.tasks_listbox.add(label)
            else:
                for task in tasks:
                    last_result = task.get("LastExecutionResult", {})
                    formatted_task = {
                        "name": task.get("Name", "Unknown"),
                        "category": task.get("Category", "Unknown"),
                        "state": task.get("State", "Unknown"),
                        "current_progress": round(
                            task.get("CurrentProgressPercentage", 0), 1
                        ),
                        "last_start": self.format_datetime(
                            last_result.get("StartTimeUtc", "")
                        ),
                        "last_end": self.format_datetime(
                            last_result.get("EndTimeUtc", "")
                        ),
                        "last_status": last_result.get("Status", "N/A"),
                    }
                    self.tasks_listbox.add(
                        self.create_task_row(formatted_task)
                    )

            self.tasks_listbox.show_all()
            return False

        threading.Thread(target=worker, daemon=True).start()

    def refresh_all(self):
        """Refresh all data."""
        self.update_statusbar("Refreshing all data...")
        self.load_server_status()
        self.load_current_processing()
        self.load_completed_tasks()
        self.load_libraries()
        self.load_movies()
        self.load_indexed_media()
        self.load_all_tasks()

    def start_refresh_timers(self):
        """Start auto-refresh timers."""
        # Refresh processing every 5 seconds
        GLib.timeout_add_seconds(
            5, lambda: (self.load_current_processing(), True)[1]
        )

        # Refresh status every 30 seconds
        GLib.timeout_add_seconds(
            30, lambda: (self.load_server_status(), True)[1]
        )
        
        # Server time update every second
        GLib.timeout_add_seconds(
            1, lambda: (self.update_server_time(), True)[1]
        )

    def update_server_time(self):
         """Update server time display."""
         now = datetime.now()
         if hasattr(self, 'time_label'):
            self.time_label.set_markup(f"<small>🕒 {now.strftime('%H:%M:%S')}</small>")

    def update_statusbar(self, message):
        """Update statusbar message."""
        self.statusbar.pop(self.statusbar_context)
        self.statusbar.push(
            self.statusbar_context,
            f"{message} - {datetime.now().strftime('%H:%M:%S')}"
        )

    def show_error_dialog(self, message):
        """Show error dialog."""
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def show_movie_details(self, movie_data):
        """Show detailed movie information dialog."""
        # Get full item details
        item_id = movie_data.get("Id")
        if not item_id:
            return

        movie = self.emby.get_item_details(item_id)
        if not movie:
            self.show_error_dialog("Failed to load movie details")
            return

        # Create dialog
        dialog = Gtk.Dialog(
            title=movie.get("Name", "Movie Details"),
            parent=self,
            flags=0,
        )
        dialog.set_default_size(900, 700)

        # Add buttons to footer
        emby_btn = dialog.add_button("🔗 Open in Emby", Gtk.ResponseType.APPLY)
        dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_border_width(10)

        # Main horizontal box (poster + details)
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        main_hbox.set_border_width(10)

        # Poster image
        poster_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        poster_box.set_size_request(300, 450)
        poster_image = Gtk.Image()
        poster_image.set_from_icon_name("video-x-generic", Gtk.IconSize.DIALOG)
        poster_box.pack_start(poster_image, True, False, 0)
        main_hbox.pack_start(poster_box, False, False, 0)

        # Load poster asynchronously
        threading.Thread(
            target=self.load_thumbnail,
            args=(item_id, poster_image, False),
            daemon=True,
        ).start()

        # Details vbox
        details_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)

        # Title and year
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_label = Gtk.Label(label=movie.get("Name", "Unknown"))
        title_label.set_halign(Gtk.Align.START)
        title_label.set_line_wrap(True)
        title_label.modify_font(Pango.FontDescription("bold 16"))
        title_box.pack_start(title_label, False, False, 0)

        if movie.get("ProductionYear"):
            year_label = Gtk.Label()
            year_label.set_markup(
                f"<span size='large' color='#666'>({movie['ProductionYear']})</span>"
            )
            title_box.pack_start(year_label, False, False, 0)

        details_vbox.pack_start(title_box, False, False, 0)

        # Genres and rating
        meta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        if movie.get("Genres"):
            genres_label = Gtk.Label()
            genres_label.set_markup(
                f"<span color='#666'>{', '.join(movie['Genres'][:3])}</span>"
            )
            meta_box.pack_start(genres_label, False, False, 0)

        if movie.get("OfficialRating"):
            rating_label = Gtk.Label()
            rating_label.set_markup(
                f"<span background='#3b82f6' foreground='white'> {movie['OfficialRating']} </span>"
            )
            meta_box.pack_start(rating_label, False, False, 0)

        details_vbox.pack_start(meta_box, False, False, 0)

        # Runtime and community rating
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        # Calculate runtime
        runtime_ticks = movie.get("RunTimeTicks", 0)
        runtime_minutes = int(runtime_ticks / 10000000 / 60) if runtime_ticks else 0
        if runtime_minutes > 0:
            hours = runtime_minutes // 60
            mins = runtime_minutes % 60
            runtime_text = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
            runtime_label = Gtk.Label()
            runtime_label.set_markup(f"<b>Runtime:</b> {runtime_text}")
            runtime_label.set_halign(Gtk.Align.START)
            info_box.pack_start(runtime_label, False, False, 0)

        if movie.get("CommunityRating"):
            comm_rating_label = Gtk.Label()
            comm_rating_label.set_markup(
                f"<b>Rating:</b> ⭐ {movie['CommunityRating']:.1f}/10"
            )
            comm_rating_label.set_halign(Gtk.Align.START)
            info_box.pack_start(comm_rating_label, False, False, 0)

        details_vbox.pack_start(info_box, False, False, 0)

        # Overview
        if movie.get("Overview"):
            overview_frame = Gtk.Frame(label="Overview")
            overview_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
            overview_label = Gtk.Label(label=movie["Overview"])
            overview_label.set_halign(Gtk.Align.START)
            overview_label.set_line_wrap(True)
            overview_label.set_max_width_chars(60)
            overview_label.set_margin_top(10)
            overview_label.set_margin_bottom(10)
            overview_label.set_margin_start(10)
            overview_label.set_margin_end(10)
            overview_frame.add(overview_label)
            details_vbox.pack_start(overview_frame, False, False, 0)

        # File information
        file_frame = Gtk.Frame(label="File Information")
        file_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        file_box.set_border_width(10)

        media_streams = movie.get("MediaStreams", [])
        video_stream = next((s for s in media_streams if s.get("Type") == "Video"), {})
        audio_streams = [s for s in media_streams if s.get("Type") == "Audio"]

        self._add_detail_row(file_box, "Path:", movie.get("Path", "N/A"))
        self._add_detail_row(file_box, "Container:", movie.get("Container", "N/A"))
        self._add_detail_row(
            file_box, "Video Codec:", video_stream.get("Codec", "N/A")
        )
        self._add_detail_row(
            file_box,
            "Resolution:",
            f"{video_stream.get('Width', 'N/A')}x{video_stream.get('Height', 'N/A')}",
        )
        self._add_detail_row(file_box, "Audio Streams:", str(len(audio_streams)))

        file_frame.add(file_box)
        details_vbox.pack_start(file_frame, False, False, 0)

        # Cast (horizontal scrolling)
        if movie.get("People"):
            actors = [p for p in movie["People"] if p.get("Type") == "Actor"][:10]
            if actors:
                cast_frame = Gtk.Frame(label="Cast")
                cast_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

                cast_scroll = Gtk.ScrolledWindow()
                cast_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
                cast_scroll.set_size_request(-1, 140)

                cast_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
                cast_hbox.set_border_width(10)

                for actor in actors:
                    actor_vbox = Gtk.Box(
                        orientation=Gtk.Orientation.VERTICAL, spacing=5
                    )

                    # Actor image
                    actor_image = Gtk.Image()
                    actor_image.set_size_request(80, 80)
                    actor_vbox.pack_start(actor_image, False, False, 0)

                    # Load actor image
                    threading.Thread(
                        target=self.load_thumbnail,
                        args=(actor.get("Id"), actor_image, True),
                        daemon=True,
                    ).start()

                    # Actor name
                    actor_name = Gtk.Label(label=actor.get("Name", ""))
                    actor_name.set_max_width_chars(12)
                    actor_name.set_line_wrap(True)
                    actor_name.set_halign(Gtk.Align.CENTER)
                    actor_name.modify_font(Pango.FontDescription("bold 9"))
                    actor_vbox.pack_start(actor_name, False, False, 0)

                    # Role
                    role_label = Gtk.Label()
                    role_label.set_markup(
                        f"<small>{actor.get('Role', 'Actor')}</small>"
                    )
                    role_label.set_max_width_chars(12)
                    role_label.set_line_wrap(True)
                    role_label.set_halign(Gtk.Align.CENTER)
                    actor_vbox.pack_start(role_label, False, False, 0)

                    cast_hbox.pack_start(actor_vbox, False, False, 0)

                cast_scroll.add(cast_hbox)
                cast_frame.add(cast_scroll)
                details_vbox.pack_start(cast_frame, False, False, 0)

        main_hbox.pack_start(details_vbox, True, True, 0)
        scrolled.add(main_hbox)

        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        dialog.show_all()

        # Handle button responses
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            # Open in Emby with correct Server ID
            import webbrowser
            
            # Get server ID
            server_id = item_id # Fallback
            sys_info = self.emby.get_system_info()
            if sys_info:
                server_id = sys_info.get("Id", item_id)
                
            emby_url = f"{config.EMBY_SERVER_URL}/web/index.html#!/item?id={item_id}&serverId={server_id}"
            webbrowser.open(emby_url)

        dialog.destroy()

    def show_server_details(self):
        """Show detailed server information dialog."""
        detailed_info = self.emby.get_detailed_server_info()

        if not detailed_info:
            self.show_error_dialog("Failed to load server details")
            return

        system_info = detailed_info.get("system", {})
        endpoint_info = detailed_info.get("endpoint", {})

        # Create dialog
        dialog = Gtk.Dialog(
            title="Server Details",
            parent=self,
            flags=0,
            buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
        )
        dialog.set_default_size(700, 600)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_border_width(10)

        # Main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.set_border_width(10)

        # System Information
        sys_frame = Gtk.Frame(label="🖥️  System Information")
        sys_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sys_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        sys_box.set_border_width(10)

        self._add_detail_row(
            sys_box, "Product:", system_info.get("ProductName", "N/A"), True
        )
        self._add_detail_row(
            sys_box, "Version:", system_info.get("Version", "N/A")
        )
        self._add_detail_row(
            sys_box, "Operating System:", system_info.get("OperatingSystem", "N/A")
        )
        self._add_detail_row(
            sys_box,
            "Architecture:",
            system_info.get("SystemArchitecture", "N/A"),
        )
        self._add_detail_row(
            sys_box, "Runtime:", system_info.get("RuntimeVersion", "N/A")
        )
        self._add_detail_row(
            sys_box, "Package:", system_info.get("PackageName", "N/A")
        )

        sys_frame.add(sys_box)
        content_box.pack_start(sys_frame, False, False, 0)

        # Network Information
        net_frame = Gtk.Frame(label="🌐  Network")
        net_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        net_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        net_box.set_border_width(10)

        self._add_detail_row(net_box, "Server ID:", system_info.get("Id", "N/A"))
        self._add_detail_row(
            net_box, "Local Address:", system_info.get("LocalAddress", "N/A")
        )
        self._add_detail_row(
            net_box, "WAN Address:", system_info.get("WanAddress", "N/A")
        )
        self._add_detail_row(
            net_box,
            "HTTP Port:",
            str(system_info.get("HttpServerPortNumber", "N/A")),
        )
        self._add_detail_row(
            net_box, "HTTPS Port:", str(system_info.get("HttpsPortNumber", "N/A"))
        )
        self._add_detail_row(
            net_box,
            "WebSocket Port:",
            str(system_info.get("WebSocketPortNumber", "N/A")),
        )

        net_frame.add(net_box)
        content_box.pack_start(net_frame, False, False, 0)

        # Paths
        path_frame = Gtk.Frame(label="📂  Paths")
        path_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        path_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        path_box.set_border_width(10)

        self._add_detail_row(
            path_box, "Program Data:", system_info.get("ProgramDataPath", "N/A")
        )
        self._add_detail_row(
            path_box, "Cache:", system_info.get("CachePath", "N/A")
        )
        self._add_detail_row(path_box, "Logs:", system_info.get("LogPath", "N/A"))
        self._add_detail_row(
            path_box, "Metadata:", system_info.get("InternalMetadataPath", "N/A")
        )
        self._add_detail_row(
            path_box, "Transcoding:", system_info.get("TranscodingTempPath", "N/A")
        )

        path_frame.add(path_box)
        content_box.pack_start(path_frame, False, False, 0)

        # Capabilities
        cap_frame = Gtk.Frame(label="⚙️  Capabilities")
        cap_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        cap_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        cap_box.set_border_width(10)

        self._add_detail_row(
            cap_box,
            "Can Self Restart:",
            "✅ Yes" if system_info.get("CanSelfRestart") else "❌ No",
        )
        self._add_detail_row(
            cap_box,
            "Can Self Update:",
            "✅ Yes" if system_info.get("CanSelfUpdate") else "❌ No",
        )
        self._add_detail_row(
            cap_box,
            "Is Local:",
            "✅ Yes" if endpoint_info.get("IsLocal") else "❌ No",
        )
        self._add_detail_row(
            cap_box,
            "Is In Network:",
            "✅ Yes" if endpoint_info.get("IsInNetwork") else "❌ No",
        )
        self._add_detail_row(
            cap_box,
            "Pending Restart:",
            "⚠️ Yes" if system_info.get("HasPendingRestart") else "✅ No",
        )
        self._add_detail_row(
            cap_box,
            "Is Shutting Down:",
            "🛑 Yes" if system_info.get("IsShuttingDown") else "✅ No",
        )

        cap_frame.add(cap_box)
        content_box.pack_start(cap_frame, False, False, 0)

        scrolled.add(content_box)
        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def _add_detail_row(self, container, label_text, value_text, bold=False):
        """Add a detail row to a container."""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label()
        label.set_markup(f"<span foreground='#666'>{label_text}</span>")
        label.set_halign(Gtk.Align.START)
        label.set_size_request(150, -1)
        row_box.pack_start(label, False, False, 0)

        value = Gtk.Label()
        if bold:
            value.set_markup(f"<b>{value_text}</b>")
        else:
            value.set_text(value_text)
        value.set_halign(Gtk.Align.START)
        value.set_line_wrap(True)
        value.set_selectable(True)
        row_box.pack_start(value, True, True, 0)

        container.pack_start(row_box, False, False, 0)


    def create_cast_tab(self):
        """Create the cast explorer tab."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_border_width(10)

        # Search bar
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search for actors, directors...")
        search_entry.connect("search-changed", self.on_cast_search_changed)
        hbox.pack_start(search_entry, True, True, 0)
        
        vbox.pack_start(hbox, False, False, 0)

        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # FlowBox for grid layout
        self.cast_flowbox = Gtk.FlowBox()
        self.cast_flowbox.set_valign(Gtk.Align.START)
        self.cast_flowbox.set_max_children_per_line(8)
        self.cast_flowbox.set_min_children_per_line(2)
        self.cast_flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.cast_flowbox.set_homogeneous(True)
        self.cast_flowbox.set_column_spacing(15)
        self.cast_flowbox.set_row_spacing(15)
        scrolled.add(self.cast_flowbox)

        vbox.pack_start(scrolled, True, True, 0)
        
        # Load initial cast
        self.load_cast()

        return vbox

    def on_cast_search_changed(self, entry):
        """Handle cast search input."""
        query = entry.get_text()
        self.load_cast(query)

    def load_cast(self, query=None):
        """Load cast members."""
        self.show_progress()
        
        # Clear existing
        for child in self.cast_flowbox.get_children():
            self.cast_flowbox.remove(child)

        def fetch_cast():
            # Correctly call get_persons with labeled arguments
            persons = self.emby.get_persons(limit=50, search_term=query)
            
            GLib.idle_add(self.populate_cast_grid, persons)

        threading.Thread(target=fetch_cast, daemon=True).start()

    def populate_cast_grid(self, persons):
        """Populate the cast flowbox with person cards."""
        self.hide_progress()
        if not persons:
            label = Gtk.Label(label="No people found.")
            label.set_sensitive(False)
            self.cast_flowbox.add(label)
            self.cast_flowbox.show_all()
            return

        for person in persons:
            card = self.create_person_card(person)
            self.cast_flowbox.add(card)
        
        self.cast_flowbox.show_all()

    def create_person_card(self, person):
        """Create a card for a person."""
        event_box = Gtk.EventBox()
        event_box.connect("button-press-event", lambda w, e: self.show_person_details(person))

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)

        # Image
        image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        image_box.set_size_request(150, 150)
        image_box.set_halign(Gtk.Align.CENTER)
        
        image = Gtk.Image()
        image.set_from_icon_name("avatar-default", Gtk.IconSize.DIALOG)
        image_box.pack_start(image, True, False, 0)
        vbox.pack_start(image_box, False, False, 0)

        if person.get("Id"):
            threading.Thread(
                target=self.load_thumbnail,
                args=(person["Id"], image, True),
                daemon=True
            ).start()

        # Name
        name_label = Gtk.Label(label=person.get("Name", "Unknown"))
        name_label.set_justify(Gtk.Justification.CENTER)
        name_label.set_line_wrap(True)
        name_label.set_max_width_chars(15)
        name_label.set_markup(f"<span weight='bold' size='10240'>{GLib.markup_escape_text(person.get('Name', 'Unknown'))}</span>")
        vbox.pack_start(name_label, False, False, 0)

        event_box.add(vbox)
        return event_box

    def show_person_details(self, person_data):
        """Show detailed person information."""
        person_id = person_data.get("Id")
        if not person_id: return

        # Fetch details
        person = self.emby.get_item_details(person_id)
        credits = self.emby.get_person_credits(person_id)

        dialog = Gtk.Dialog(
            title=person.get("Name", "Person Details"),
            parent=self,
            flags=0,
            buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        )
        dialog.set_default_size(800, 600)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_border_width(10)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_border_width(10)

        # Header: Image + Bio info
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        
        # Image
        img_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        img_box.set_size_request(200, 300)
        image = Gtk.Image()
        image.set_from_icon_name("avatar-default", Gtk.IconSize.DIALOG)
        img_box.pack_start(image, False, False, 0)
        hbox.pack_start(img_box, False, False, 0)
        
        threading.Thread(
             target=self.load_thumbnail,
             args=(person_id, image, True),
             daemon=True
        ).start()

        # Info
        info_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        name = Gtk.Label(label=person.get("Name"))
        name.set_halign(Gtk.Align.START)
        name.modify_font(Pango.FontDescription("bold 18"))
        info_vbox.pack_start(name, False, False, 0)

        if person.get("PremiereDate"):
             bdate = self.format_datetime(person["PremiereDate"]).split(' ')[0]
             born = Gtk.Label()
             born.set_markup(f"<b>Born:</b> {bdate}")
             born.set_halign(Gtk.Align.START)
             info_vbox.pack_start(born, False, False, 0)

        if person.get("ProductionLocations"):
             place = Gtk.Label()
             place.set_markup(f"<b>Place of Birth:</b> {person['ProductionLocations'][0]}")
             place.set_halign(Gtk.Align.START)
             info_vbox.pack_start(place, False, False, 0)

        if person.get("Overview"):
            bio_scroll = Gtk.ScrolledWindow()
            bio_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            bio_scroll.set_size_request(-1, 150)
            
            bio = Gtk.Label(label=person["Overview"])
            bio.set_line_wrap(True)
            bio.set_halign(Gtk.Align.START)
            bio.set_valign(Gtk.Align.START)
            bio.set_selectable(True)
            bio_scroll.add(bio)
            info_vbox.pack_start(bio_scroll, True, True, 0)

        hbox.pack_start(info_vbox, True, True, 0)
        content_box.pack_start(hbox, False, False, 0)

        # Credits (Appears In)
        if credits:
            credits_frame = Gtk.Frame(label="Appears In")
            credits_scroll = Gtk.ScrolledWindow()
            credits_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
            credits_scroll.set_size_request(-1, 220)
            
            credits_flow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
            credits_flow.set_border_width(10)

            for credit in credits:
                 # Minimal movie card
                 card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                 card.set_size_request(120, -1)
                 
                 c_img = Gtk.Image()
                 c_img.set_from_icon_name("video-x-generic", Gtk.IconSize.DIALOG)
                 c_img.set_pixel_size(100) # approximate
                 card.pack_start(c_img, False, False, 0)
                 
                 if credit.get("Id"):
                     threading.Thread(
                         target=self.load_thumbnail,
                         args=(credit["Id"], c_img, False),
                         daemon=True
                     ).start()

                 c_title = Gtk.Label(label=credit.get("Name", ""))
                 c_title.set_line_wrap(True)
                 c_title.set_justify(Gtk.Justification.CENTER)
                 c_title.modify_font(Pango.FontDescription("9"))
                 card.pack_start(c_title, False, False, 0)

                 credits_flow.pack_start(card, False, False, 0)

            credits_scroll.add(credits_flow)
            credits_frame.add(credits_scroll)
            content_box.pack_start(credits_frame, True, True, 0)

        scrolled.add(content_box)
        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()


def main():
    """Main entry point for GTK application."""
    app = EmbyMonitorApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
