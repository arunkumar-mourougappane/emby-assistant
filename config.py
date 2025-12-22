"""
Configuration loader for Emby Assistant application.
Loads configuration from environment variables or .env file.
"""
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Emby server configuration
EMBY_SERVER_URL = os.getenv('EMBY_SERVER_URL', 'http://localhost:8096')
EMBY_API_KEY = os.getenv('EMBY_API_KEY', '')

# Flask configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Refresh intervals (in seconds)
PROCESSING_REFRESH_INTERVAL = int(os.getenv('PROCESSING_REFRESH_INTERVAL', 5))
STATUS_REFRESH_INTERVAL = int(os.getenv('STATUS_REFRESH_INTERVAL', 30))


def validate_config():
    """Validate that required configuration is present."""
    if not EMBY_API_KEY:
        raise ValueError(
            "EMBY_API_KEY is not set. "
            "Please create a .env file with your API key.\n"
            "You can generate an API key from: "
            "Emby Dashboard -> Advanced -> API Keys"
        )

    if not EMBY_SERVER_URL:
        raise ValueError("EMBY_SERVER_URL is not set")

    return True
