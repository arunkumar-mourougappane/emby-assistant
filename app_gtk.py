#!/usr/bin/env python3
"""GTK Desktop Application for Emby Server Monitoring."""

# Standard library imports
import threading
from datetime import datetime

# Third-party imports
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
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
        super().__init__(title="Emby Server Monitor")

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

        # Tab 3: Indexed Media
        media_box = self.create_media_tab()
        notebook.append_page(media_box, Gtk.Label(label="🎬 Indexed Media"))

        # Tab 4: All Tasks
        tasks_box = self.create_all_tasks_tab()
        notebook.append_page(tasks_box, Gtk.Label(label="📋 All Tasks"))

        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context = self.statusbar.get_context_id("main")
        main_vbox.pack_start(self.statusbar, False, False, 0)

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

        vbox.pack_start(info_box, False, False, 0)

        # Refresh button
        refresh_btn = Gtk.Button(label="🔄 Refresh All")
        refresh_btn.connect("clicked", lambda w: self.refresh_all())
        vbox.pack_start(refresh_btn, False, False, 5)

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

        title = Gtk.Label(label=task["name"])
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title.modify_font(Pango.FontDescription("bold 11"))
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Details
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)

        cat_label = Gtk.Label()
        cat_label.set_markup(f"<small>Category: {task['category']}</small>")
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

    def create_media_row(self, item):
        """Create a row for a media item."""
        row = Gtk.ListBoxRow()

        # Main horizontal box to hold thumbnail and content
        main_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        main_hbox.set_border_width(10)

        # Thumbnail placeholder (will be loaded asynchronously)
        if item["type"] in ["Movie", "Video"] and item.get("id"):
            thumbnail_image = Gtk.Image()
            thumbnail_image.set_size_request(100, 150)
            thumbnail_image.set_from_icon_name(
                "video-x-generic", Gtk.IconSize.DIALOG
            )
            main_hbox.pack_start(thumbnail_image, False, False, 0)

            # Load thumbnail asynchronously
            threading.Thread(
                target=self.load_thumbnail,
                args=(item["id"], thumbnail_image),
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

        title = Gtk.Label(label=display_name)
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title.modify_font(Pango.FontDescription("bold 10"))
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

        title = Gtk.Label(label=task["name"])
        title.set_halign(Gtk.Align.START)
        title.set_line_wrap(True)
        title.modify_font(Pango.FontDescription("bold 10"))
        title_box.pack_start(title, False, False, 0)

        vbox.pack_start(title_box, False, False, 0)

        # Category
        cat_label = Gtk.Label()
        cat_label.set_markup(f"<small>Category: {task['category']}</small>")
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

    def load_thumbnail(self, item_id, image_widget):
        """Load thumbnail image for a media item asynchronously."""
        try:
            # Get image URL from Emby
            image_url = (
                f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/"
                f"Images/Primary?maxHeight=150&maxWidth=100&quality=90"
            )

            # Download image
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

                # Scale image to fit
                if pixbuf:
                    width = pixbuf.get_width()
                    height = pixbuf.get_height()

                    # Maintain aspect ratio
                    if height > 150:
                        new_height = 150
                        new_width = int(width * (150 / height))
                    else:
                        new_width = width
                        new_height = height

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

        def update_ui():
            system_info = self.emby.get_system_info()

            if not system_info:
                self.status_indicator.set_markup(
                    "<span size='large' foreground='red'>⚫</span>"
                )
                self.server_name_label.set_markup(
                    "<span foreground='red'>Could not connect to server</span>"
                )
                return False

            self.status_indicator.set_markup(
                "<span size='large' foreground='green'>🟢</span>"
            )
            self.server_name_label.set_markup(
                f"<b>{system_info.get('ServerName', 'Unknown')}</b>"
            )
            self.version_label.set_text(
                f"Version: {system_info.get('Version', 'Unknown')}"
            )
            self.os_label.set_text(
                f"OS: {system_info.get('OperatingSystem', 'Unknown')}"
            )

            self.update_statusbar("Server status updated")
            return False

        threading.Thread(
            target=lambda: GLib.idle_add(update_ui), daemon=True
        ).start()

    def load_current_processing(self):
        """Load currently processing media."""

        def update_ui():
            processing = self.emby.get_processing_media()

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

        threading.Thread(
            target=lambda: GLib.idle_add(update_ui), daemon=True
        ).start()

    def load_completed_tasks(self):
        """Load recently completed tasks."""

        def update_ui():
            completed = self.emby.get_completed_tasks(limit=15)

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

        threading.Thread(
            target=lambda: GLib.idle_add(update_ui), daemon=True
        ).start()

    def load_indexed_media(self):
        """Load indexed media."""

        def update_ui():
            # Get limit from combo box
            limits = {0: 50, 1: 100, 2: 200}
            limit = limits.get(self.media_limit_combo.get_active(), 50)

            items = self.emby.get_recently_added(limit=limit)

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
            return False

        threading.Thread(
            target=lambda: GLib.idle_add(update_ui), daemon=True
        ).start()

    def load_all_tasks(self):
        """Load all scheduled tasks."""

        def update_ui():
            tasks = self.emby.get_scheduled_tasks()

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

        threading.Thread(
            target=lambda: GLib.idle_add(update_ui), daemon=True
        ).start()

    def refresh_all(self):
        """Refresh all data."""
        self.update_statusbar("Refreshing all data...")
        self.load_server_status()
        self.load_current_processing()
        self.load_completed_tasks()
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


def main():
    """Main entry point for GTK application."""
    app = EmbyMonitorApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
