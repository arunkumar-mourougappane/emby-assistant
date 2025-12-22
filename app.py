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
    """Proxy images from Emby server."""
    try:
        import requests

        image_url = (
            f"{config.EMBY_SERVER_URL}/emby/Items/{item_id}/Images/Primary"
        )
        params = {"maxHeight": 150, "maxWidth": 100, "quality": 90}
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
