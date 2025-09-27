import cv2
import numpy as np
from flask import Flask, Response, render_template_string
import threading
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Global camera variable
camera = None
camera_lock = threading.Lock()

def get_camera():
    global camera
    with camera_lock:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            if camera.isOpened():
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("✅ Camera initialized successfully!")
            else:
                print("❌ Could not open camera - using placeholder")
    return camera

def generate_frames():
    camera = get_camera()
    
    # Load face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    while True:
        if camera and camera.isOpened():
            success, frame = camera.read()
            if not success:
                break
        else:
            # Create a placeholder frame if camera fails
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "Camera Not Available", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            success = True
        
        if success:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f'Face {len(faces)}', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Add frame counter
            cv2.putText(frame, f'Faces detected: {len(faces)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Attendance System - Face Detection</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f0f2f5; }
        .container { max-width: 1000px; margin: 0 auto; }
        .card { background: white; padding: 25px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 5px; }
        .success { color: #28a745; font-weight: bold; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .feature-item { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .camera-feed { border: 3px solid #007bff; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🎯 AI-Powered Attendance System</h1>
            <p class="success">✅ Real-time Face Detection Active</p>
            <p>Using OpenCV's advanced computer vision algorithms</p>
        </div>

        <div class="card">
            <h2>👁️ Live Face Detection</h2>
            <div class="camera-feed">
                <img src="/video_feed" width="640" height="480">
            </div>
            <p>Green rectangles indicate detected faces using Haar Cascade classifier</p>
        </div>

        <div class="feature-grid">
            <div class="feature-item">
                <h3>📊 Database</h3>
                <p>SQLite + Student Management</p>
                <a href="/test_db" class="btn">Test</a>
            </div>
            <div class="feature-item">
                <h3>👥 Students</h3>
                <p>View Registered Users</p>
                <a href="/students" class="btn">View</a>
            </div>
            <div class="feature-item">
                <h3>🤖 AI Features</h3>
                <p>Computer Vision</p>
                <span class="btn" style="background: #28a745;">Active</span>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
        return f'''
        <div style="font-family: Arial; margin: 40px;">
            <h2>Database Status</h2>
            <p><strong>Tables:</strong> {tables}</p>
            <p><strong>Students Registered:</strong> {student_count}</p>
            <p><strong>Face Detection:</strong> Active (OpenCV Haar Cascade)</p>
            <a href="/" class="btn">Back to Dashboard</a>
        </div>
        '''
    except Exception as e:
        return f'<div style="font-family: Arial; margin: 40px;"><h2>Error</h2><p>{str(e)}</p><a href="/">Back</a></div>'

@app.route('/students')
def view_students():
    try:
        conn = sqlite3.connect('attendance_simple.db')
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name, email FROM students;")
        students = cursor.fetchall()
        conn.close()
        
        student_list = "<h2>Registered Students</h2><ul>"
        for student in students:
            student_list += f"<li><strong>{student[1]}</strong> (ID: {student[0]}) - {student[2]}</li>"
        student_list += "</ul>"
        
        return f'<div style="font-family: Arial; margin: 40px;">{student_list}<a href="/">Back</a></div>'
    except Exception as e:
        return f'<div style="font-family: Arial; margin: 40px;"><h2>Error</h2><p>{str(e)}</p><a href="/">Back</a></div>'

if __name__ == '__main__':
    print("🚀 AI Attendance System with Face Detection Starting...")
    print("📷 Live camera feed: http://localhost:5000")
    print("🤖 Face detection using OpenCV Haar Cascade")
    print("💡 Green rectangles will show detected faces")
    app.run(debug=True)
