import openai
import requests
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import OPENAI_API_KEY, WEATHER_API_KEY, DATABASE_NAME
import sys

# Import agent classes
from agent.WeatherAgent import WeatherAgent
from agent.EventAgent import EventAgent
from agent.RecommendationAgent import RecommendationAgent

class CoordinatorAgent:
    """Main coordinator that orchestrates all agents."""
    
    def __init__(self, weather_api_key: str, openai_api_key: str):
        self.weather_agent = WeatherAgent(weather_api_key)
        self.event_agent = EventAgent()
        self.recommendation_agent = RecommendationAgent(openai_api_key)
    
    def get_recommendations(self, location: str, date: str, event_type: Optional[str] = None) -> str:
        """
        Get event recommendations for a specific location and date.
        
        Args:
            location: City name
            date: Date in YYYY-MM-DD format
            event_type: Optional filter for event type
            verbose: Whether to print progress messages
            
        Returns:
            String containing recommendations or error message
        """
        try:
            # Step 1: Fetch weather data
            print(f"\n🌤️  Fetching weather data for {location} on {date}...")
            weather_data = self.weather_agent.get_weather(location, date)
            
            # Step 2: Retrieve events
            print("📅 Fetching events from database...")
            events = self.event_agent.get_events(date, event_type)
            
            if not events:
                return f"❌ No events found for {date}."
            
            print(f"✓ Found {len(events)} event(s)")
            
            # Step 3: Generate recommendations
            print("🤖 Generating AI recommendations...")
            recommendations = self.recommendation_agent.generate_recommendation(
                weather_data, events
            )
            
            return recommendations
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
