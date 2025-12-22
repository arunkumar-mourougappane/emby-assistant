"""Flask web application for Emby monitoring."""

# Standard library imports
from datetime import datetime

# Third-party imports
from flask import Flask, jsonify, render_template, request

# Local imports
import config
from emby_client import EmbyClient

app = Flask(__name__)

# Initialize Emby client
emby = None


def get_emby_client() -> EmbyClient:
    """Get or create Emby client instance."""
    global emby
    if emby is None:
        emby = EmbyClient(config.EMBY_SERVER_URL, config.EMBY_API_KEY)
    return emby


def format_datetime(dt_str: str) -> str:
    """Format datetime string to readable format."""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return dt_str


def calculate_duration(start_str: str, end_str: str) -> str:
    """Calculate duration between start and end times."""
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


@app.route("/")
def index():
    """Main page."""
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    """Get server status."""
    client = get_emby_client()
    system_info = client.get_system_info()

    if not system_info:
        return jsonify({"error": "Could not connect to Emby server"}), 500

    return jsonify(
        {
            "server_name": system_info.get("ServerName", "Unknown"),
            "version": system_info.get("Version", "Unknown"),
            "operating_system": system_info.get("OperatingSystem", "Unknown"),
            "is_shutting_down": system_info.get("IsShuttingDown", False),
            "has_pending_restart": system_info.get("HasPendingRestart", False),
            "can_self_restart": system_info.get("CanSelfRestart", False),
        }
    )


@app.route("/api/server-details")
def get_server_details():
    """Get detailed server information."""
    client = get_emby_client()
    detailed_info = client.get_detailed_server_info()

    if not detailed_info:
        return jsonify({"error": "Could not connect to Emby server"}), 500

    system_info = detailed_info.get("system", {})
    endpoint_info = detailed_info.get("endpoint", {})

    # Format the response
    return jsonify(
        {
            "server_name": system_info.get("ServerName", "Unknown"),
            "version": system_info.get("Version", "Unknown"),
            "product_name": system_info.get("ProductName", "Emby Server"),
            "operating_system": system_info.get("OperatingSystem", "Unknown"),
            "system_architecture": system_info.get("SystemArchitecture", "Unknown"),
            "runtime_version": system_info.get("RuntimeVersion", "Unknown"),

            # Server ID and Status
            "id": system_info.get("Id", "Unknown"),
            "local_address": system_info.get("LocalAddress", "Unknown"),
            "wan_address": system_info.get("WanAddress", "Unknown"),
            "is_shutting_down": system_info.get("IsShuttingDown", False),
            "has_pending_restart": system_info.get("HasPendingRestart", False),
            "can_self_restart": system_info.get("CanSelfRestart", False),
            "can_self_update": system_info.get("CanSelfUpdate", False),

            # Transcoding
            "transcoding_temp_path": system_info.get("TranscodingTempPath", "N/A"),
            "hardware_acceleration_type": system_info.get(
                "HardwareAccelerationRequiresVirtualization", "N/A"
            ),

            # Cache and Logs
            "cache_path": system_info.get("CachePath", "N/A"),
            "log_path": system_info.get("LogPath", "N/A"),
            "internal_metadata_path": system_info.get("InternalMetadataPath", "N/A"),

            # Endpoint info
            "is_local": endpoint_info.get("IsLocal", False),
            "is_in_network": endpoint_info.get("IsInNetwork", False),

            # Package and program data
            "package_name": system_info.get("PackageName", "N/A"),
            "program_data_path": system_info.get("ProgramDataPath", "N/A"),
            "web_socket_port_number": system_info.get("WebSocketPortNumber", "N/A"),
            "http_server_port_number": system_info.get(
                "HttpServerPortNumber", "N/A"
            ),
            "https_port_number": system_info.get("HttpsPortNumber", "N/A"),
            "completed_installations": system_info.get(
                "CompletedInstallations", []
            ),
        }
    )


@app.route("/api/current-processing")
def get_current_processing():
    """Get currently processing media."""
    client = get_emby_client()
    processing = client.get_processing_media()

    # Format the data for display
    formatted = []
    for item in processing:
        formatted.append(
            {
                "task_name": item.get("task_name", "Unknown"),
                "state": item.get("state", "Unknown"),
                "progress": round(item.get("progress", 0), 1),
                "category": item.get("category", "Unknown"),
                "description": item.get("description", ""),
                "started_at": format_datetime(
                    item.get("last_execution_time", "")
                ),
            }
        )

    return jsonify(formatted)


@app.route("/api/completed-tasks")
def get_completed_tasks():
    """Get recently completed tasks."""
    client = get_emby_client()
    completed = client.get_completed_tasks(limit=15)

    # Format the data
    formatted = []
    for task in completed:
        formatted.append(
            {
                "name": task.get("name", "Unknown"),
                "category": task.get("category", "Unknown"),
                "status": task.get("status", "Unknown"),
                "completed_at": format_datetime(task.get("end_time", "")),
                "duration": calculate_duration(
                    task.get("start_time", ""), task.get("end_time", "")
                ),
            }
        )

    return jsonify(formatted)


@app.route("/api/indexed-media")
def get_indexed_media():
    """Get recently indexed media."""
    client = get_emby_client()
    limit = request.args.get("limit", 50, type=int)

    items = client.get_recently_added(limit=limit)

    # Format the data
    formatted = []
    for item in items:
        formatted.append(
            {
                "name": item.get("Name", "Unknown"),
                "type": item.get("Type", "Unknown"),
                "added_at": format_datetime(item.get("DateCreated", "")),
                "path": item.get("Path", "N/A"),
                "id": item.get("Id", ""),
                "series_name": item.get("SeriesName", ""),
                "season": item.get("ParentIndexNumber", ""),
                "episode": item.get("IndexNumber", ""),
            }
        )

    return jsonify(formatted)


@app.route("/api/all-tasks")
def get_all_tasks():
    """Get all scheduled tasks."""
    client = get_emby_client()
    tasks = client.get_scheduled_tasks()

    if not tasks:
        return jsonify([])

    formatted = []
    for task in tasks:
        last_result = task.get("LastExecutionResult", {})
        formatted.append(
            {
                "id": task.get("Id", ""),
                "name": task.get("Name", "Unknown"),
                "category": task.get("Category", "Unknown"),
                "state": task.get("State", "Unknown"),
                "current_progress": round(
                    task.get("CurrentProgressPercentage", 0), 1
                ),
                "last_start": format_datetime(
                    last_result.get("StartTimeUtc", "")
                ),
                "last_end": format_datetime(last_result.get("EndTimeUtc", "")),
                "last_status": last_result.get("Status", "N/A"),
            }
        )

    return jsonify(formatted)


@app.route("/api/image/<item_id>")
def get_image(item_id):
    """Proxy images from Emby server with fallback to thumbnails."""
    try:
        import requests

        # Use higher quality settings and preserve aspect ratio
        # Only set maxHeight to avoid distortion
        params = {"maxHeight": 450, "quality": 95}

        # Try Primary image first
        image_url = (
            f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/Images/Primary"
        )
        response = requests.get(
            image_url,
            params=params,
            headers={"X-Emby-Token": config.EMBY_API_KEY},
            timeout=5
        )

        # If Primary image not found, try Thumb
        if response.status_code == 404:
            image_url = (
                f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/Images/Thumb"
            )
            response = requests.get(
                image_url,
                params=params,
                headers={"X-Emby-Token": config.EMBY_API_KEY},
                timeout=5
            )

        if response.status_code == 200:
            from flask import Response  # type: ignore

            return Response(
                response.content,
                mimetype=response.headers.get("Content-Type", "image/jpeg"),
            )
        return "", 404
    except Exception:
        return "", 404


@app.route("/api/person-image/<person_id>")
def get_person_image(person_id):
    """Proxy person images from Emby server with fallback to thumbnails."""
    try:
        import requests

        # Use higher quality settings and preserve aspect ratio
        params = {"maxHeight": 200, "quality": 95}

        # Try Primary image first
        image_url = (
            f"{config.EMBY_SERVER_URL}/emby/Items/{person_id}/Images/Primary"
        )
        response = requests.get(
            image_url,
            params=params,
            headers={"X-Emby-Token": config.EMBY_API_KEY},
            timeout=5
        )

        # If Primary image not found, try Thumb
        if response.status_code == 404:
            image_url = (
                f"{config.EMBY_SERVER_URL}/emby/Items/{person_id}/Images/Thumb"
            )
            response = requests.get(
                image_url,
                params=params,
                headers={"X-Emby-Token": config.EMBY_API_KEY},
                timeout=5
            )

        if response.status_code == 200:
            from flask import Response  # type: ignore

            return Response(
                response.content,
                mimetype=response.headers.get("Content-Type", "image/jpeg"),
            )
        return "", 404
    except Exception:
        return "", 404


@app.route("/api/libraries")
def get_libraries():
    """Get all media libraries."""
    client = get_emby_client()
    libraries = client.get_libraries()

    # Filter to only include movie libraries
    movie_libraries = []
    for lib in libraries:
        # Check if library contains movies
        if lib.get("CollectionType") == "movies":
            movie_libraries.append(
                {
                    "id": lib.get("ItemId", ""),
                    "name": lib.get("Name", "Unknown"),
                    "collection_type": lib.get("CollectionType", ""),
                }
            )

    return jsonify(movie_libraries)


@app.route("/api/movies")
def get_movies():
    """Get movies with metadata, optionally filtered by library."""
    client = get_emby_client()
    limit = request.args.get("limit", 100, type=int)
    sort_by = request.args.get("sortBy", "SortName")
    sort_order = request.args.get("sortOrder", "Ascending")
    library_id = request.args.get("libraryId", None)

    # Use the new method that supports library filtering
    movies = client.get_movies_by_library(
        parent_id=library_id, limit=limit, sort_by=sort_by, sort_order=sort_order
    )

    # Format the data - only include movies with valid IDs
    formatted = []
    for movie in movies:
        # Skip movies without IDs (shouldn't happen but just in case)
        movie_id = movie.get("Id", "")
        if not movie_id:
            continue

        # Calculate runtime
        runtime_ticks = movie.get("RunTimeTicks", 0)
        runtime_minutes = int(runtime_ticks / 10000000 / 60) if runtime_ticks else 0

        formatted.append(
            {
                "id": movie_id,
                "name": movie.get("Name", "Unknown"),
                "year": movie.get("ProductionYear", ""),
                "overview": movie.get("Overview", ""),
                "genres": movie.get("Genres", []),
                "community_rating": movie.get("CommunityRating", 0),
                "official_rating": movie.get("OfficialRating", ""),
                "runtime_minutes": runtime_minutes,
                "path": movie.get("Path", "N/A"),
                "premiere_date": format_datetime(movie.get("PremiereDate", "")),
                "date_created": format_datetime(movie.get("DateCreated", "")),
                "people": movie.get("People", [])[:5],  # Limit to top 5 cast
                "parent_id": movie.get("ParentId", ""),
            }
        )

    return jsonify(formatted)


@app.route("/api/item/<item_id>")
def get_item_details(item_id):
    """Get detailed information about a specific item."""
    client = get_emby_client()
    item = client.get_item_details(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Calculate runtime
    runtime_ticks = item.get("RunTimeTicks", 0)
    runtime_minutes = int(runtime_ticks / 10000000 / 60) if runtime_ticks else 0

    # Get media streams info
    media_streams = item.get("MediaStreams", [])
    video_stream = next((s for s in media_streams if s.get("Type") == "Video"), {})
    audio_streams = [s for s in media_streams if s.get("Type") == "Audio"]

    return jsonify(
        {
            "id": item.get("Id", ""),
            "name": item.get("Name", "Unknown"),
            "type": item.get("Type", "Unknown"),
            "year": item.get("ProductionYear", ""),
            "overview": item.get("Overview", ""),
            "genres": item.get("Genres", []),
            "community_rating": item.get("CommunityRating", 0),
            "official_rating": item.get("OfficialRating", ""),
            "runtime_minutes": runtime_minutes,
            "path": item.get("Path", "N/A"),
            "premiere_date": format_datetime(item.get("PremiereDate", "")),
            "date_created": format_datetime(item.get("DateCreated", "")),
            "people": item.get("People", []),
            "video_codec": video_stream.get("Codec", "N/A"),
            "video_resolution": f"{video_stream.get('Width', 'N/A')}x{video_stream.get('Height', 'N/A')}",
            "audio_streams": len(audio_streams),
            "container": item.get("Container", "N/A"),
        }
    )


@app.template_filter("format_datetime")
def format_datetime_filter(dt_str):
    """Template filter for formatting datetime."""
    return format_datetime(dt_str)


if __name__ == "__main__":
    try:
        config.validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        exit(1)

    print(
        f"Starting Emby Assistant on "
        f"http://{config.FLASK_HOST}:{config.FLASK_PORT}"
    )
    print(f"Connecting to Emby server at: {config.EMBY_SERVER_URL}")

    app.run(
        debug=config.FLASK_DEBUG,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT
    )
