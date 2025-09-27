import sqlite3
from datetime import datetime
import os

class SimpleAttendanceDB:
    def __init__(self, db_name='attendance_simple.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Initialize database tables using only SQLite (no pandas)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                date TEXT,
                time_in TEXT,
                status TEXT DEFAULT 'Present'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def add_student(self, student_id, name, email):
        """Add student without face recognition for now"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, email)
                VALUES (?, ?, ?)
            ''', (student_id, name, email))
            conn.commit()
            print(f"✅ Student {name} added successfully!")
            return True
        except sqlite3.IntegrityError:
            print("❌ Student ID already exists!")
            return False
        finally:
            conn.close()

# Test the simple database
if __name__ == '__main__':
    db = SimpleAttendanceDB()
    
    # Add a test student
    db.add_student("TEST001", "John Doe", "john@test.com")
    
    print("🎉 Simple attendance system is working!")
    print("You can now install packages gradually.")