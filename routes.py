import os
import shutil
import sqlite3
import pandas as pd
from flask import Blueprint, render_template, Response, stream_with_context, jsonify, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app.camera import VideoCamera

main = Blueprint('main', __name__)
camera = VideoCamera()

UPLOAD_FOLDER = 'dataset'

# 🔹 Landing Page (Welcome with Get Started)
@main.route('/')
def landing_page():
    return render_template('landing.html')


# 🔹 Face Recognition Home Page
@main.route('/frs')
def index():
    return render_template('index.html')


# 🔹 Live Video Feed Route
@main.route('/video_feed')
def video_feed():
    return Response(stream_with_context(generate_frames()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_frames():
    while True:
        frame = camera.get_frames()
        yield frame


# 🔹 Attendance Table Page
@main.route('/attendance')
def attendance_page():
    return render_template('attendance.html')


# 🔹 API: Return Attendance JSON (with optional date filter)
@main.route('/api/attendance')
def get_attendance_data():
    date = request.args.get('date')
    query = "SELECT name, time FROM attendance"
    params = ()

    if date:
        query += " WHERE DATE(time) = ?"
        params = (date,)

    query += " ORDER BY time DESC"

    conn = sqlite3.connect('db/attendance.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    data = [{"name": name, "time": time} for name, time in rows]
    return jsonify(data)


# 🔹 API: Recognize Once via Button
@main.route('/api/recognize')
def recognize_once():
    success, frame = camera.video.read()
    if not success:
        return jsonify({"names": [], "message": "Camera read failed."})

    recognized_names = camera.recognizer.get_names_only(frame)
    return jsonify({
        "names": recognized_names,
        "message": f"Recognized: {', '.join(recognized_names) if recognized_names else 'No known face.'}"
    })


# 🔹 CSV Export Page
@main.route('/download')
def download_csv_page():
    db_path = 'db/attendance.db'
    csv_path = 'attendance_export.csv'

    if not os.path.exists(db_path):
        return render_template("download_result.html", message="Database not found.", records=[])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, time FROM attendance ORDER BY time DESC")
    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=['Name', 'Time'])
    df.to_csv(csv_path, index=False)

    return render_template("download_result.html", message="CSV Exported Successfully!", records=rows)


# 🔹 Register Form Page
@main.route('/register')
def register():
    people = [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]
    return render_template('register.html', registered_people=people, registered_count=len(people))


# 🔹 Handle Image Upload for Face Registration
@main.route('/upload_images', methods=['POST'])
def upload_images():
    name = request.form.get('name')
    files = request.files.getlist('images')

    if not name or len(files) < 3:
        return "Please provide a name and at least 3 images.", 400

    user_folder = os.path.join(UPLOAD_FOLDER, name)
    os.makedirs(user_folder, exist_ok=True)

    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(user_folder, filename))

    # Optional: os.system("python encode_faces.py")

    return f"Images uploaded successfully for {name}. Now go to /encode or restart app to re-encode."


# 🔹 Delete Face Data (Folder)
@main.route('/delete_face', methods=['POST'])
def delete_face():
    person_name = request.form.get('person_name')
    person_folder = os.path.join(UPLOAD_FOLDER, person_name)

    if os.path.exists(person_folder) and os.path.isdir(person_folder):
        shutil.rmtree(person_folder)
        flash(f"Deleted face data for {person_name}.", "success")
    else:
        flash(f"No folder found for {person_name}.", "danger")

    return redirect(url_for('main.register'))


# 🔹 DELETE Attendance Record API
@main.route('/api/delete_attendance', methods=['DELETE'])
def delete_attendance():
    data = request.get_json()
    name = data.get('name')
    time = data.get('time')

    if not name or not time:
        return jsonify({'error': 'Invalid data'}), 400

    conn = sqlite3.connect('db/attendance.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE name = ? AND time = ?", (name, time))
    conn.commit()
    conn.close()

    return jsonify({'success': True}), 200
