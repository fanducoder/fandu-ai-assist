import openai
import requests
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import OPENAI_API_KEY, WEATHER_API_KEY, DATABASE_NAME
import sys

class WeatherAgent:
    """Agent responsible for fetching and processing weather data."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
    
    def get_weather(self, location: str, date: str) -> Dict:
        """
        Fetch weather data for a specific location and date.
        
        Args:
            location: City name or coordinates
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing weather data
        """
        # Determine if we need current or forecast weather
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_diff = (target_date - today).days
        
        try:
            if days_diff == 0:
                # Use current weather for today
                url = f"{self.base_url}/current.json"
                params = {
                    "key": self.api_key,
                    "q": location,
                    "aqi": "no"
                }
            elif 0 < days_diff <= 14:
                # Use forecast for future dates (up to 14 days)
                url = f"{self.base_url}/forecast.json"
                params = {
                    "key": self.api_key,
                    "q": location,
                    "days": days_diff + 1,
                    "aqi": "no"
                }
            else:
                # Past dates or far future - use current as fallback
                url = f"{self.base_url}/current.json"
                params = {"key": self.api_key, "q": location, "aqi": "no"}
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant forecast day if using forecast API
            if 'forecast' in data and days_diff > 0:
                forecast_day = data['forecast']['forecastday'][days_diff]
                return {
                    'location': data['location'],
                    'current': forecast_day['day'],
                    'condition': forecast_day['day']['condition'],
                    'is_forecast': True
                }
            
            return data
            
        except requests.exceptions.Timeout:
            raise Exception(f"Weather API timeout for location: {location}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise Exception(f"Invalid location: {location}")
            elif e.response.status_code == 401:
                raise Exception("Invalid Weather API key")
            else:
                raise Exception(f"Weather API error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error fetching weather: {str(e)}")
    