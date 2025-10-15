# config.py
# Configuration file for API keys
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# WeatherAPI.com Configuration  
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Google Search API Key  
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")

# Database configuration
DATABASE_NAME = "events.db"

# Validate that required API keys are present
def validate_config():
    """Validate that all required environment variables are set."""
    missing_vars = []
    
    if not OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    
    if not WEATHER_API_KEY:
        missing_vars.append("WEATHER_API_KEY")
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please set them in your environment or create a .env file.\n"
        )
    
    return True

