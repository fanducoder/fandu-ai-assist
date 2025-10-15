import openai
import requests
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import OPENAI_API_KEY, WEATHER_API_KEY, DATABASE_NAME
import sys

class RecommendationAgent:
    """Agent responsible for generating AI-powered recommendations."""
    
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        openai.api_key = openai_api_key
    
    def generate_recommendation(self, weather_data: Dict, events: List[Tuple]) -> str:
        """
        Generate event recommendations based on weather and available events.
        
        Args:
            weather_data: Weather information dictionary
            events: List of event tuples
            
        Returns:
            String containing the recommendation
        """
        if not events:
            return "No events available for the selected date."
        
        # Build context for GPT
        context = self._build_context(weather_data, events)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an intelligent event recommendation assistant. 
                        Analyze weather conditions and available events to provide personalized recommendations.
                        
                        Guidelines:
                        - Prioritize outdoor events for pleasant weather (20-28°C, clear/partly cloudy)
                        - Recommend indoor events for extreme temperatures, rain, or poor conditions
                        - Consider event timing with weather conditions
                        - Mention practical tips (bring umbrella, wear sunscreen, etc.)
                        - Be concise but informative (3-4 sentences per recommendation)
                        - If multiple suitable events exist, rank them with brief reasoning
                        """
                    },
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except openai.error.AuthenticationError:
            raise Exception("Invalid OpenAI API key")
        except openai.error.RateLimitError:
            raise Exception("OpenAI API rate limit exceeded. Please try again later.")
        except openai.error.APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Recommendation generation error: {str(e)}")
    
    def _build_context(self, weather_data: Dict, events: List[Tuple]) -> str:
        """Build formatted context string for GPT."""
        context_parts = []
        
        # Weather information
        if 'current' in weather_data:
            current = weather_data['current']
            location = weather_data.get('location', {})
            
            if 'temp_c' in current:
                # Current weather format
                condition = current.get('condition', {}).get('text', 'Unknown')
                temp = current.get('temp_c', 'N/A')
                humidity = current.get('humidity', 'N/A')
                
                context_parts.append(f"Location: {location.get('name', 'Unknown')}")
                context_parts.append(f"Weather: {condition}")
                context_parts.append(f"Temperature: {temp}°C")
                context_parts.append(f"Humidity: {humidity}%")
                
                if 'is_forecast' in weather_data:
                    context_parts.append("(Forecast data)")
            else:
                # Forecast day format
                condition = current.get('condition', {}).get('text', 'Unknown')
                avg_temp = current.get('avgtemp_c', 'N/A')
                max_temp = current.get('maxtemp_c', 'N/A')
                min_temp = current.get('mintemp_c', 'N/A')
                
                context_parts.append(f"Weather Forecast: {condition}")
                context_parts.append(f"Temperature: {min_temp}°C - {max_temp}°C (avg: {avg_temp}°C)")
        else:
            context_parts.append("Weather: Data unavailable")
        
        # Events information
        context_parts.append("\nAvailable Events:")
        for event in events:
            _, name, event_type, desc, loc, date, time, price = event
            time_str = f" at {time}" if time else ""
            price_str = f" ({price})" if price else ""
            context_parts.append(
                f"- {name} ({event_type.upper()}){time_str}: {desc} | Location: {loc}{price_str}"
            )
        
        return "\n".join(context_parts)


