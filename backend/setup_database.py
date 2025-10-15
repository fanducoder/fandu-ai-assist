import sqlite3
from datetime import datetime, timedelta

def setup_database():
    """Create and populate the events database with sample data."""
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    
    # Create events table
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('indoor', 'outdoor')),
            description TEXT,
            location TEXT,
            date TEXT NOT NULL,
            time TEXT,
            price_range TEXT
        )
    ''')
    
    # Clear existing data for fresh start
    c.execute('DELETE FROM events')
    
    # Generate sample events with varied dates
    base_date = datetime.now()
    
    events = [
        # Today's events
        ('Summer Concert', 'outdoor', 'Live music in the park', 'Central Park', 
         base_date.strftime('%Y-%m-%d'), '18:00', 'Free'),
        ('Art Exhibition', 'indoor', 'Modern art showcase', 'City Gallery', 
         base_date.strftime('%Y-%m-%d'), '10:00', '$15-25'),
        
        # Tomorrow's events
        ('Food Festival', 'outdoor', 'International cuisine', 'Waterfront', 
         (base_date + timedelta(days=1)).strftime('%Y-%m-%d'), '11:00', '$20-50'),
        ('Theater Show', 'indoor', 'Classical drama', 'Grand Theater', 
         (base_date + timedelta(days=1)).strftime('%Y-%m-%d'), '19:30', '$30-80'),
        
        # Day after tomorrow
        ('Yoga in the Park', 'outdoor', 'Morning yoga session', 'Botanical Gardens', 
         (base_date + timedelta(days=2)).strftime('%Y-%m-%d'), '07:00', 'Free'),
        ('Museum Tour', 'indoor', 'Historical artifacts exhibition', 'National Museum', 
         (base_date + timedelta(days=2)).strftime('%Y-%m-%d'), '14:00', '$10-20'),
        
        # Additional varied events
        ('Night Market', 'outdoor', 'Street food and crafts', 'Market Square', 
         (base_date + timedelta(days=3)).strftime('%Y-%m-%d'), '17:00', 'Free entry'),
        ('Jazz Night', 'indoor', 'Live jazz performance', 'Blue Note Club', 
         (base_date + timedelta(days=3)).strftime('%Y-%m-%d'), '20:00', '$25-40'),
    ]
    
    c.executemany('''
        INSERT INTO events (name, type, description, location, date, time, price_range) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', events)
    
    conn.commit()
    
    # Verify data
    c.execute('SELECT COUNT(*) FROM events')
    count = c.fetchone()[0]
    print(f"✓ Database setup complete! {count} events added.")
    
    # Show sample data
    c.execute('SELECT date, COUNT(*) FROM events GROUP BY date ORDER BY date')
    date_counts = c.fetchall()
    print("\nEvents by date:")
    for date, count in date_counts:
        print(f"  {date}: {count} event(s)")
    
    conn.close()

if __name__ == "__main__":
    setup_database()
