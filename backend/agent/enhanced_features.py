"""
Enhanced features and extensions for the recommendation system.
This module demonstrates additional capabilities beyond the base requirements.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from recommendation_system import CoordinatorAgent, EventAgent
from config import WEATHER_API_KEY, OPENAI_API_KEY, DATABASE_NAME


class EnhancedEventAgent(EventAgent):
    """Extended EventAgent with additional filtering capabilities."""
    
    def get_events_by_price_range(self, date: str, max_price: float) -> List[Tuple]:
        """
        Get events within a specific price range.
        
        Args:
            date: Date in YYYY-MM-DD format
            max_price: Maximum price willing to pay
            
        Returns:
            List of events within price range
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT id, name, type, description, location, date, time, price_range 
                FROM events 
                WHERE date = ? AND (
                    price_range LIKE '%Free%' 
                    OR price_range LIKE '%$0%'
                    OR CAST(SUBSTR(price_range, 2, INSTR(price_range, '-') - 2) AS REAL) <= ?
                )
                ORDER BY time
            ''', (date, max_price))
            
            return c.fetchall()
        finally:
            conn.close()
    
    def get_events_by_time_period(self, date: str, period: str) -> List[Tuple]:
        """
        Get events by time of day.
        
        Args:
            date: Date in YYYY-MM-DD format
            period: 'morning' (before 12), 'afternoon' (12-17), 'evening' (after 17)
            
        Returns:
            List of events in the specified time period
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            if period == 'morning':
                time_filter = "time < '12:00'"
            elif period == 'afternoon':
                time_filter = "time >= '12:00' AND time < '17:00'"
            elif period == 'evening':
                time_filter = "time >= '17:00'"
            else:
                raise ValueError("Period must be 'morning', 'afternoon', or 'evening'")
            
            query = f'''
                SELECT id, name, type, description, location, date, time, price_range 
                FROM events 
                WHERE date = ? AND {time_filter}
                ORDER BY time
            '''
            
            c.execute(query, (date,))
            return c.fetchall()
        finally:
            conn.close()
    
    def search_events(self, keyword: str, date: Optional[str] = None) -> List[Tuple]:
        """
        Search events by keyword in name or description.
        
        Args:
            keyword: Search term
            date: Optional date filter
            
        Returns:
            List of matching events
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            keyword_pattern = f"%{keyword}%"
            
            if date:
                c.execute('''
                    SELECT id, name, type, description, location, date, time, price_range 
                    FROM events 
                    WHERE (name LIKE ? OR description LIKE ?) AND date = ?
                    ORDER BY date, time
                ''', (keyword_pattern, keyword_pattern, date))
            else:
                c.execute('''
                    SELECT id, name, type, description, location, date, time, price_range 
                    FROM events 
                    WHERE name LIKE ? OR description LIKE ?
                    ORDER BY date, time
                ''', (keyword_pattern, keyword_pattern))
            
            return c.fetchall()
        finally:
            conn.close()


class ItineraryAgent:
    """Agent for generating multi-day itineraries."""
    
    def __init__(self, coordinator: CoordinatorAgent):
        self.coordinator = coordinator
        self.event_agent = EnhancedEventAgent()
    
    def generate_weekend_plan(self, location: str, start_date: str) -> Dict[str, str]:
        """
        Generate a weekend activity plan (Friday-Sunday).
        
        Args:
            location: City name
            start_date: Starting date (should be a Friday)
            
        Returns:
            Dictionary with daily recommendations
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        plan = {}
        
        for i in range(3):  # Friday, Saturday, Sunday
            current_date = (start + timedelta(days=i)).strftime('%Y-%m-%d')
            day_name = (start + timedelta(days=i)).strftime('%A')
            
            recommendations = self.coordinator.get_recommendations(
                location, current_date
            )
            
            plan[f"{day_name} ({current_date})"] = recommendations
        
        return plan
    
    def generate_daily_schedule(self, location: str, date: str) -> Dict[str, List[Tuple]]:
        """
        Generate a full-day schedule with morning, afternoon, and evening activities.
        
        Args:
            location: City name
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with events organized by time period
        """
        schedule = {
            'morning': self.event_agent.get_events_by_time_period(date, 'morning'),
            'afternoon': self.event_agent.get_events_by_time_period(date, 'afternoon'),
            'evening': self.event_agent.get_events_by_time_period(date, 'evening')
        }
        
        return schedule


class StatisticsAgent:
    """Agent for generating statistics and insights."""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
    
    def get_event_summary(self) -> Dict:
        """Get overall statistics about events in database."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            # Total events
            c.execute("SELECT COUNT(*) FROM events")
            total = c.fetchone()[0]
            
            # Events by type
            c.execute("SELECT type, COUNT(*) FROM events GROUP BY type")
            by_type = dict(c.fetchall())
            
            # Events by date
            c.execute("""
                SELECT date, COUNT(*) 
                FROM events 
                GROUP BY date 
                ORDER BY date
            """)
            by_date = dict(c.fetchall())
            
            # Upcoming events
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COUNT(*) FROM events WHERE date >= ?", (today,))
            upcoming = c.fetchone()[0]
            
            return {
                'total_events': total,
                'by_type': by_type,
                'by_date': by_date,
                'upcoming_events': upcoming
            }
        finally:
            conn.close()
    
    def get_popular_locations(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most popular event locations."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute("""
                SELECT location, COUNT(*) as count 
                FROM events 
                GROUP BY location 
                ORDER BY count DESC 
                LIMIT ?
            """, (limit,))
            
            return c.fetchall()
        finally:
            conn.close()
    
    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_event_summary()
        
        print("\n" + "=" * 60)
        print("📊 EVENT DATABASE STATISTICS")
        print("=" * 60)
        print(f"\nTotal Events: {stats['total_events']}")
        print(f"Upcoming Events: {stats['upcoming_events']}")
        
        print("\n📍 Events by Type:")
        for event_type, count in stats['by_type'].items():
            print(f"  {event_type.capitalize()}: {count}")
        
        print("\n📅 Events by Date:")
        for date, count in sorted(stats['by_date'].items())[:7]:  # Show next 7 days
            print(f"  {date}: {count} event(s)")
        
        print("\n🏆 Popular Locations:")
        locations = self.get_popular_locations()
        for i, (location, count) in enumerate(locations, 1):
            print(f"  {i}. {location} ({count} events)")
        
        print("=" * 60)


def demo_enhanced_features():
    """Demonstrate enhanced features."""
    print("=" * 70)
    print("🚀 ENHANCED FEATURES DEMONSTRATION")
    print("=" * 70)
    
    # Statistics
    stats_agent = StatisticsAgent()
    stats_agent.print_statistics()
    
    # Enhanced event filtering
    print("\n" + "=" * 70)
    print("🔍 ENHANCED EVENT FILTERING")
    print("=" * 70)
    
    enhanced_agent = EnhancedEventAgent()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Search by keyword
    print("\n🔎 Searching for 'music' events...")
    music_events = enhanced_agent.search_events('music')
    print(f"Found {len(music_events)} event(s) matching 'music'")
    for event in music_events[:3]:
        print(f"  - {event[1]} on {event[5]}")
    
    # Filter by time period
    print("\n🌅 Evening events today:")
    evening_events = enhanced_agent.get_events_by_time_period(today, 'evening')
    if evening_events:
        for event in evening_events:
            print(f"  - {event[1]} at {event[6]} ({event[4]})")
    else:
        print("  No evening events found for today")
    
    # Multi-day itinerary
    print("\n" + "=" * 70)
    print("📅 WEEKEND ITINERARY GENERATOR")
    print("=" * 70)
    
    try:
        coordinator = CoordinatorAgent(WEATHER_API_KEY, OPENAI_API_KEY)
        itinerary_agent = ItineraryAgent(coordinator)
        
        # Find next Friday
        today_dt = datetime.now()
        days_until_friday = (4 - today_dt.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        next_friday = today_dt + timedelta(days=days_until_friday)
        
        print(f"\nGenerating weekend plan starting {next_friday.strftime('%Y-%m-%d')}...")
        print("(This may take a moment as it fetches weather and generates AI recommendations)\n")
        
        weekend_plan = itinerary_agent.generate_weekend_plan(
            "Singapore", 
            next_friday.strftime('%Y-%m-%d')
        )
        
        for day, recommendation in weekend_plan.items():
            print(f"\n{day}:")
            print("-" * 70)
            print(recommendation)
    
    except Exception as e:
        print(f"⚠️  Could not generate itinerary: {e}")
        print("(Make sure your API keys are configured in config.py)")
    
    # Daily schedule
    print("\n" + "=" * 70)
    print("⏰ DAILY SCHEDULE ORGANIZER")
    print("=" * 70)
    
    schedule = itinerary_agent.generate_daily_schedule("Singapore", today)
    
    for period, events in schedule.items():
        print(f"\n{period.upper()}:")
        if events:
            for event in events:
                print(f"  {event[6]} - {event[1]} at {event[4]} ({event[2]})")
        else:
            print(f"  No {period} events scheduled")


if __name__ == "__main__":
    demo_enhanced_features()
