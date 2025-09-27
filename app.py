from flask import Flask, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Attendance System</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .success { color: green; font-weight: bold; }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI-Powered Attendance System</h1>
        <p class="success">Database is working! System ready for development.</p>
        
        <h2>Features:</h2>
        <ul>
            <li>SQLite Database</li>
            <li>Flask Web Framework</li>
            <li>Face Recognition (Next)</li>
            <li>Real-time Tracking (Next)</li>
        </ul>
        
        <div>
            <a href="/test_db" class="btn">Test Database</a>
            <a href="/students" class="btn">View Students</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test_db')
def test_db():
    try:
        conn = sqlite3.connect('attendance_simple.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM students;")
        student_count = cursor.fetchone()[0]
        
        conn.close()
        return f"Database working!<br>Tables: {tables}<br>Students registered: {student_count}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/students')
def view_students():
    try:
        conn = sqlite3.connect('attendance_simple.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name, email FROM students;")
        students = cursor.fetchall()
        conn.close()
        
        student_list = "<h2>Registered Students:</h2><ul>"
        for student in students:
            student_list += f"<li>{student[1]} ({student[0]}) - {student[2]}</li>"
        student_list += "</ul>"
        
        return student_list
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    print("Starting AI Attendance System...")
    print("Open: http://localhost:5000")
    app.run(debug=True)
