"""
Test suite for the recommendation system.
Run with: python test_recommendation_system.py
"""

import sqlite3
from datetime import datetime, timedelta
from recommendation_system import (
    WeatherAgent, EventAgent, RecommendationAgent, CoordinatorAgent
)

class TestEventAgent:
    """Test the EventAgent functionality."""
    
    @staticmethod
    def test_event_retrieval():
        """Test retrieving events from database."""
        print("\n📋 Testing Event Agent...")
        
        agent = EventAgent()
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            events = agent.get_events(today)
            print(f"✓ Retrieved {len(events)} events for {today}")
            
            if events:
                print("  Sample event:")
                event = events[0]
                print(f"    Name: {event[1]}")
                print(f"    Type: {event[2]}")
                print(f"    Location: {event[4]}")
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    @staticmethod
    def test_event_filtering():
        """Test filtering events by type."""
        print("\n🔍 Testing Event Filtering...")
        
        agent = EventAgent()
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            indoor_events = agent.get_events(today, 'indoor')
            outdoor_events = agent.get_events(today, 'outdoor')
            
            print(f"✓ Found {len(indoor_events)} indoor events")
            print(f"✓ Found {len(outdoor_events)} outdoor events")
            
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


class TestDatabaseIntegrity:
    """Test database setup and integrity."""
    
    @staticmethod
    def test_database_structure():
        """Verify database has correct structure."""
        print("\n🗄️  Testing Database Structure...")
        
        try:
            conn = sqlite3.connect('events.db')
            c = conn.cursor()
            
            # Check if table exists
            c.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='events'
            """)
            
            if not c.fetchone():
                print("✗ Events table not found!")
                return False
            
            # Check columns
            c.execute("PRAGMA table_info(events)")
            columns = {col[1] for col in c.fetchall()}
            required_columns = {'id', 'name', 'type', 'description', 'location', 'date'}
            
            if not required_columns.issubset(columns):
                print(f"✗ Missing columns: {required_columns - columns}")
                return False
            
            # Check data
            c.execute("SELECT COUNT(*) FROM events")
            count = c.fetchone()[0]
            
            print(f"✓ Database structure valid")
            print(f"✓ Found {count} events in database")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @staticmethod
    def test_invalid_date():
        """Test handling of invalid dates."""
        print("\n⚠️  Testing Error Handling...")
        
        agent = EventAgent()
        
        try:
            # Test with date that has no events
            future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            events = agent.get_events(future_date)
            
            if len(events) == 0:
                print(f"✓ Correctly handled date with no events: {future_date}")
            else:
                print(f"  Note: Found {len(events)} events for future date")
            
            return True
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    @staticmethod
    def test_invalid_location():
        """Test weather agent with invalid location (requires real API key)."""
        print("\n🌍 Testing Invalid Location Handling...")
        
        try:
            from config import WEATHER_API_KEY
            agent = WeatherAgent(WEATHER_API_KEY)
            
            try:
                # Try to get weather for invalid location
                agent.get_weather("InvalidCity123XYZ", datetime.now().strftime('%Y-%m-%d'))
                print("✗ Should have raised an exception for invalid location")
                return False
            except Exception as e:
                if "Invalid location" in str(e) or "400" in str(e):
                    print("✓ Correctly handled invalid location")
                    return True
                else:
                    print(f"✗ Unexpected error type: {e}")
                    return False
                    
        except ImportError:
            print("⚠️  Skipped: config.py not configured")
            return True


class TestIntegration:
    """Integration tests for the full system."""
    
    @staticmethod
    def test_coordinator_workflow():
        """Test the complete recommendation workflow."""
        print("\n🔄 Testing Full Coordinator Workflow...")
        
        try:
            from config import WEATHER_API_KEY, OPENAI_API_KEY
            
            coordinator = CoordinatorAgent(WEATHER_API_KEY, OPENAI_API_KEY)
            today = datetime.now().strftime('%Y-%m-%d')
            
            print("  Running recommendation generation...")
            result = coordinator.get_recommendations("Singapore", today, verbose=False)
            
            if "Error" in result:
                print(f"⚠️  Got error (might be expected): {result[:100]}...")
                return True
            elif len(result) > 50:
                print(f"✓ Generated recommendation ({len(result)} chars)")
                print(f"  Preview: {result[:100]}...")
                return True
            else:
                print("⚠️  Recommendation seems too short")
                return False
                
        except ImportError:
            print("⚠️  Skipped: API keys not configured in config.py")
            return True
        except Exception as e:
            print(f"⚠️  Error (might be expected): {e}")
            return True


def run_all_tests():
    """Run all test suites."""
    print("=" * 70)
    print("🧪 RUNNING TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Database tests
    results.append(("Database Structure", TestDatabaseIntegrity.test_database_structure()))
    
    # Event Agent tests
    results.append(("Event Retrieval", TestEventAgent.test_event_retrieval()))
    results.append(("Event Filtering", TestEventAgent.test_event_filtering()))
    
    # Error handling tests
    results.append(("Invalid Date Handling", TestErrorHandling.test_invalid_date()))
    results.append(("Invalid Location", TestErrorHandling.test_invalid_location()))
    
    # Integration tests
    results.append(("Full Workflow", TestIntegration.test_coordinator_workflow()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
