"""Emby API Client for interacting with Emby server."""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class EmbyClient:
    """Client for interacting with Emby server API."""
    
    def __init__(self, server_url: str, api_key: str):
        """
        Initialize Emby client.
        
        Args:
            server_url: Base URL of the Emby server (e.g., http://localhost:8096)
            api_key: API key for authentication
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict] = None) -> Optional[Dict]:
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
            response = requests.request(method, url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def get_system_info(self) -> Optional[Dict]:
        """Get server system information and status."""
        return self._make_request('/emby/System/Info')
    
    def get_scheduled_tasks(self) -> Optional[List[Dict]]:
        """Get all scheduled tasks/jobs."""
        return self._make_request('/emby/ScheduledTasks')
    
    def get_active_tasks(self) -> List[Dict]:
        """Get currently running/active tasks."""
        tasks = self.get_scheduled_tasks()
        if not tasks:
            return []
        
        active_tasks = []
        for task in tasks:
            if task.get('State') in ['Running', 'Cancelling']:
                active_tasks.append(task)
        
        return active_tasks
    
    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Get detailed information about a specific task."""
        return self._make_request(f'/emby/ScheduledTasks/{task_id}')
    
    def get_library_items(self, limit: int = 100, sort_by: str = 'DateCreated', 
                         sort_order: str = 'Descending') -> Optional[Dict]:
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
            'Recursive': 'true',
            'Limit': limit,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'Fields': 'DateCreated,Path,MediaStreams,Overview'
        }
        return self._make_request('/emby/Items', params=params)
    
    def get_recently_added(self, limit: int = 20) -> List[Dict]:
        """Get recently added/indexed media items."""
        result = self.get_library_items(limit=limit, sort_by='DateCreated')
        if result and 'Items' in result:
            return result['Items']
        return []
    
    def get_activity_log(self, limit: int = 50) -> Optional[Dict]:
        """Get server activity log."""
        params = {
            'Limit': limit,
            'HasUserId': 'false'
        }
        return self._make_request('/emby/System/ActivityLog/Entries', params=params)
    
    def get_processing_media(self) -> List[Dict]:
        """
        Get media that is currently being processed.
        This includes scanning, metadata refresh, etc.
        """
        active_tasks = self.get_active_tasks()
        processing_info = []
        
        for task in active_tasks:
            task_name = task.get('Name', '')
            current_progress = task.get('CurrentProgressPercentage', 0)
            state = task.get('State', '')
            
            # Extract media info from task description or current item
            media_info = {
                'task_name': task_name,
                'state': state,
                'progress': current_progress,
                'category': task.get('Category', 'Unknown'),
                'description': task.get('Description', ''),
                'last_execution_time': task.get('LastExecutionResult', {}).get('StartTimeUtc', ''),
                'id': task.get('Id', '')
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
            if task.get('State') == 'Idle' and task.get('LastExecutionResult'):
                last_result = task['LastExecutionResult']
                if last_result.get('Status') == 'Completed':
                    completed.append({
                        'name': task.get('Name', ''),
                        'end_time': last_result.get('EndTimeUtc', ''),
                        'start_time': last_result.get('StartTimeUtc', ''),
                        'status': last_result.get('Status', ''),
                        'category': task.get('Category', ''),
                    })
        
        # Sort by end time
        completed.sort(key=lambda x: x.get('end_time', ''), reverse=True)
        return completed[:limit]
