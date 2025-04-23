import sqlite3
import datetime
import os
import json

class AnalyticsManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database with necessary tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create daily metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date TEXT PRIMARY KEY,
            screen_time_minutes REAL,
            blink_count INTEGER,
            avg_distance REAL,
            good_posture_percentage REAL,
            exercises_completed INTEGER
        )
        ''')
        
        # Create hourly metrics table for more detailed analysis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS hourly_metrics (
            datetime TEXT PRIMARY KEY,
            screen_time_minutes REAL,
            blink_count INTEGER,
            avg_distance REAL,
            good_posture_percentage REAL
        )
        ''')
        
        # Create session logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT,
            end_time TEXT,
            duration_minutes REAL,
            blink_rate REAL,
            avg_distance REAL,
            notes TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def update_metrics(self, screen_time_minutes, blink_count, distance, posture_good):
        """Update analytics data with current metrics"""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        hour = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if daily record exists
            cursor.execute("SELECT * FROM daily_metrics WHERE date = ?", (today,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing record
                cursor.execute('''
                UPDATE daily_metrics SET
                    screen_time_minutes = screen_time_minutes + ?,
                    blink_count = blink_count + ?,
                    avg_distance = (avg_distance + ?) / 2,
                    good_posture_percentage = (good_posture_percentage + ?) / 2
                WHERE date = ?
                ''', (
                    screen_time_minutes, blink_count, distance, 
                    100 if posture_good else 0, today
                ))
            else:
                # Insert new record
                cursor.execute('''
                INSERT INTO daily_metrics (
                    date, screen_time_minutes, blink_count, avg_distance, 
                    good_posture_percentage, exercises_completed
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    today, screen_time_minutes, blink_count, distance,
                    100 if posture_good else 0, 0
                ))
            
            # Same for hourly metrics
            cursor.execute("SELECT * FROM hourly_metrics WHERE datetime = ?", (hour,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                UPDATE hourly_metrics SET
                    screen_time_minutes = screen_time_minutes + ?,
                    blink_count = blink_count + ?,
                    avg_distance = (avg_distance + ?) / 2,
                    good_posture_percentage = (good_posture_percentage + ?) / 2
                WHERE datetime = ?
                ''', (
                    screen_time_minutes, blink_count, distance, 
                    100 if posture_good else 0, hour
                ))
            else:
                cursor.execute('''
                INSERT INTO hourly_metrics (
                    datetime, screen_time_minutes, blink_count, avg_distance, 
                    good_posture_percentage
                ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    hour, screen_time_minutes, blink_count, distance,
                    100 if posture_good else 0
                ))
            
            conn.commit()
        except Exception as e:
            print(f"Error updating metrics: {e}")
        finally:
            conn.close()
    
    def log_exercise(self):
        """Log completed exercise"""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if daily record exists
            cursor.execute("SELECT * FROM daily_metrics WHERE date = ?", (today,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                UPDATE daily_metrics SET exercises_completed = exercises_completed + 1
                WHERE date = ?
                ''', (today,))
            else:
                cursor.execute('''
                INSERT INTO daily_metrics (
                    date, screen_time_minutes, blink_count, avg_distance, 
                    good_posture_percentage, exercises_completed
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (today, 0, 0, 0, 0, 1))
            
            conn.commit()
        except Exception as e:
            print(f"Error logging exercise: {e}")
        finally:
            conn.close()
    
    def get_analytics_data(self, days=7):
        """Get analytics data for the specified number of days"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        try:
            cursor.execute('''
            SELECT date, screen_time_minutes, blink_count, avg_distance, 
                   good_posture_percentage, exercises_completed
            FROM daily_metrics
            WHERE date BETWEEN ? AND ?
            ORDER BY date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            daily_data = [dict(row) for row in cursor.fetchall()]
            
            # Get hourly data for today
            today = end_date.strftime('%Y-%m-%d')
            cursor.execute('''
            SELECT datetime, screen_time_minutes, blink_count, avg_distance, good_posture_percentage
            FROM hourly_metrics
            WHERE datetime LIKE ?
            ORDER BY datetime
            ''', (f"{today}%",))
            
            hourly_data = [dict(row) for row in cursor.fetchall()]
            
            # Calculate averages and totals
            if daily_data:
                totals = {
                    'total_screen_time': sum(day['screen_time_minutes'] for day in daily_data),
                    'total_blinks': sum(day['blink_count'] for day in daily_data),
                    'avg_distance': sum(day['avg_distance'] for day in daily_data) / len(daily_data),
                    'avg_posture': sum(day['good_posture_percentage'] for day in daily_data) / len(daily_data),
                    'total_exercises': sum(day['exercises_completed'] for day in daily_data)
                }
            else:
                totals = {
                    'total_screen_time': 0,
                    'total_blinks': 0,
                    'avg_distance': 0,
                    'avg_posture': 0,
                    'total_exercises': 0
                }
            
            return {
                'daily': daily_data,
                'hourly': hourly_data,
                'totals': totals
            }
        except Exception as e:
            print(f"Error getting analytics data: {e}")
            return {
                'daily': [],
                'hourly': [],
                'totals': {
                    'total_screen_time': 0,
                    'total_blinks': 0,
                    'avg_distance': 0,
                    'avg_posture': 0,
                    'total_exercises': 0
                }
            }
        finally:
            conn.close()
