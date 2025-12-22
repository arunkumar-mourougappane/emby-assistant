"""Emby API Client for interacting with Emby server."""

# Standard library imports
from typing import Dict, List, Optional

# Third-party imports
import requests


class EmbyClient:
    """Client for interacting with Emby server API."""

    def __init__(self, server_url: str, api_key: str):
        """
        Initialize Emby client.

        Args:
            server_url: Base URL of the Emby server
                (e.g., http://localhost:8096)
            api_key: API key for authentication
        """
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Emby-Token": api_key,
            "Content-Type": "application/json"
        }

    def _make_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make a request to the Emby API.

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters

        Returns:
            JSON response or None on error
        """
        url = f"{self.server_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, params=params, timeout=10
            )
            # Only raise for server errors (5xx), not client errors like 404
            if response.status_code >= 500:
                response.raise_for_status()
            # Return None for 404 (not found) without printing error
            if response.status_code == 404:
                return None
            # For other client errors (4xx), check if we got valid JSON
            if response.status_code >= 400:
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            # Only print error for non-404 errors
            if not (hasattr(e, 'response') and e.response and e.response.status_code == 404):
                print(f"Error making request to {url}: {e}")
            return None

    def get_system_info(self) -> Optional[Dict]:
        """Get server system information and status."""
        return self._make_request("/emby/System/Info")

    def get_detailed_server_info(self) -> Optional[Dict]:
        """Get detailed server information including drives and endpoint info."""
        system_info = self.get_system_info()
        if not system_info:
            return None

        # Get additional endpoint information
        endpoint_info = self._make_request("/emby/System/Endpoint")

        # Combine all information
        detailed_info = {
            "system": system_info,
            "endpoint": endpoint_info or {}
        }

        return detailed_info

    def get_scheduled_tasks(self) -> Optional[List[Dict]]:
        """Get all scheduled tasks/jobs."""
        result = self._make_request("/emby/ScheduledTasks")
        if result is None:
            return None
        if isinstance(result, list):
            return result
        return None

    def get_active_tasks(self) -> List[Dict]:
        """Get currently running/active tasks."""
        tasks = self.get_scheduled_tasks()
        if not tasks:
            return []

        active_tasks = []
        for task in tasks:
            if task.get("State") in ["Running", "Cancelling"]:
                active_tasks.append(task)

        return active_tasks

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get detailed information about a specific task."""
        return self._make_request(f"/emby/ScheduledTasks/{task_id}")

    def get_library_items(
        self,
        limit: int = 100,
        sort_by: str = "DateCreated",
        sort_order: str = "Descending",
    ) -> Optional[Dict]:
        """
        Get library items (recently added/indexed media).

        Args:
            limit: Maximum number of items to return
            sort_by: Field to sort by
            sort_order: Sort order (Ascending/Descending)

        Returns:
            Dictionary containing items and total count
        """
        params = {
            "Recursive": "true",
            "Limit": limit,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Fields": "DateCreated,Path,MediaStreams,Overview",
        }
        return self._make_request("/emby/Items", params=params)

    def get_recently_added(self, limit: int = 20) -> List[Dict]:
        """Get recently added/indexed media items."""
        result = self.get_library_items(limit=limit, sort_by="DateCreated")
        if result and "Items" in result:
            return result["Items"]
        return []

    def get_activity_log(self, limit: int = 50) -> Optional[Dict]:
        """Get server activity log."""
        params = {"Limit": limit, "HasUserId": "false"}
        return self._make_request(
            "/emby/System/ActivityLog/Entries", params=params
        )

    def get_processing_media(self) -> List[Dict]:
        """
        Get media that is currently being processed.
        This includes scanning, metadata refresh, etc.
        """
        active_tasks = self.get_active_tasks()
        processing_info = []

        for task in active_tasks:
            task_name = task.get("Name", "")
            current_progress = task.get("CurrentProgressPercentage", 0)
            state = task.get("State", "")

            # Extract media info from task description or current item
            media_info = {
                "task_name": task_name,
                "state": state,
                "progress": current_progress,
                "category": task.get("Category", "Unknown"),
                "description": task.get("Description", ""),
                "last_execution_time": task.get("LastExecutionResult", {}).get(
                    "StartTimeUtc", ""
                ),
                "id": task.get("Id", ""),
            }

            processing_info.append(media_info)

        return processing_info

    def get_completed_tasks(self, limit: int = 10) -> List[Dict]:
        """Get recently completed tasks."""
        all_tasks = self.get_scheduled_tasks()
        if not all_tasks:
            return []

        completed = []
        for task in all_tasks:
            if task.get("State") == "Idle" and task.get("LastExecutionResult"):
                last_result = task["LastExecutionResult"]
                if last_result.get("Status") == "Completed":
                    completed.append(
                        {
                            "name": task.get("Name", ""),
                            "end_time": last_result.get("EndTimeUtc", ""),
                            "start_time": last_result.get("StartTimeUtc", ""),
                            "status": last_result.get("Status", ""),
                            "category": task.get("Category", ""),
                        }
                    )

        # Sort by end time
        completed.sort(key=lambda x: x.get("end_time", ""), reverse=True)
        return completed[:limit]

    def get_movies(
        self,
        limit: int = 100,
        sort_by: str = "SortName",
        sort_order: str = "Ascending",
    ) -> List[Dict]:
        """
        Get all movies with detailed metadata.

        Args:
            limit: Maximum number of movies to return
            sort_by: Field to sort by (SortName, DateCreated, PremiereDate, etc.)
            sort_order: Sort order (Ascending/Descending)

        Returns:
            List of movies with full metadata
        """
        params = {
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            "Limit": limit,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Fields": "Path,MediaStreams,Overview,Genres,People,CommunityRating,OfficialRating,RunTimeTicks,ProductionYear,PremiereDate,DateCreated",
        }
        result = self._make_request("/emby/Items", params=params)
        if result and "Items" in result:
            return result["Items"]
        return []

    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific item.

        Args:
            item_id: The item ID

        Returns:
            Detailed item information including metadata
        """
        return self._make_request(f"/emby/Items/{item_id}")

    def get_libraries(self) -> List[Dict]:
        """
        Get all media libraries (virtual folders).

        Returns:
            List of libraries with their metadata
        """
        result = self._make_request("/emby/Library/VirtualFolders")
        if result and isinstance(result, list):
            return result
        return []

    def get_movies_by_library(
        self,
        parent_id: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "SortName",
        sort_order: str = "Ascending",
    ) -> List[Dict]:
        """
        Get movies filtered by library with detailed metadata.

        Args:
            parent_id: Library/folder ID to filter by (None for all movies)
            limit: Maximum number of movies to return
            sort_by: Field to sort by (SortName, DateCreated, PremiereDate, etc.)
            sort_order: Sort order (Ascending/Descending)

        Returns:
            List of movies with full metadata
        """
        params = {
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            "Limit": limit,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Fields": "Path,MediaStreams,Overview,Genres,People,CommunityRating,OfficialRating,RunTimeTicks,ProductionYear,PremiereDate,DateCreated,ParentId",
        }

        # Add parent ID filter if specified
        if parent_id:
            params["ParentId"] = parent_id

        result = self._make_request("/emby/Items", params=params)
        if result and "Items" in result:
            return result["Items"]
        return []
