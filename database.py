import sqlite3
import pandas as pd
from datetime import datetime
import os

class AttendanceDB:
    def __init__(self, db_name='attendance_system.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT,
                face_encoding BLOB,
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
                time_out TEXT,
                status TEXT DEFAULT 'Present',
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_student(self, student_id, name, email, face_encoding):
        """Add a new student to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, email, face_encoding)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, email, face_encoding))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_student_by_id(self, student_id):
        """Retrieve student by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        student = cursor.fetchone()
        conn.close()
        
        return student
    
    def get_all_students(self):
        """Get all registered students"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT student_id, name, email FROM students', conn)
        conn.close()
        return df
    
    def mark_attendance(self, student_id, status='Present'):
        """Mark attendance for a student"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Check if already marked today
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND date = ?
        ''', (student_id, today))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update time_out
            cursor.execute('''
                UPDATE attendance SET time_out = ? 
                WHERE student_id = ? AND date = ?
            ''', (current_time, student_id, today))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO attendance (student_id, date, time_in, status)
                VALUES (?, ?, ?, ?)
            ''', (student_id, today, current_time, status))
        
        conn.commit()
        conn.close()
    
    def get_attendance_report(self, start_date=None, end_date=None):
        """Generate attendance report"""
        conn = sqlite3.connect(self.db_name)
        
        query = '''
            SELECT s.name, s.student_id, a.date, a.time_in, a.time_out, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
        '''
        
        params = []
        if start_date and end_date:
            query += ' WHERE a.date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

# Test the database
if __name__ == '__main__':
    db = AttendanceDB()
    print("Database initialized successfully!")