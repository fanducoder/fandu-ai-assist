import openai
import requests
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import OPENAI_API_KEY, WEATHER_API_KEY, DATABASE_NAME
import sys

class EventAgent:
    """Agent responsible for managing and querying event data."""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
    
    def get_events(self, date: str, event_type: Optional[str] = None) -> List[Tuple]:
        """
        Retrieve events from database for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            event_type: Optional filter for 'indoor' or 'outdoor'
            
        Returns:
            List of event tuples
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            if event_type and event_type in ['indoor', 'outdoor']:
                c.execute('''
                    SELECT id, name, type, description, location, date, time, price_range 
                    FROM events 
                    WHERE date = ? AND type = ?
                    ORDER BY time
                ''', (date, event_type))
            else:
                c.execute('''
                    SELECT id, name, type, description, location, date, time, price_range 
                    FROM events 
                    WHERE date = ?
                    ORDER BY time
                ''', (date,))
            
            events = c.fetchall()
            return events
            
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_all_upcoming_events(self, days: int = 7) -> List[Tuple]:
        """Get all events for the next N days."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute('''
                SELECT id, name, type, description, location, date, time, price_range 
                FROM events 
                WHERE date >= ?
                ORDER BY date, time
                LIMIT ?
            ''', (today, days * 10))  # Reasonable limit
            
            return c.fetchall()
        finally:
            conn.close()
