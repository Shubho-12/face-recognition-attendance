import face_recognition
import pickle
import cv2
import os
import sqlite3
from datetime import datetime


class Recognizer:
    def __init__(self):
        if not os.path.exists("models/encodings.pkl"):
            raise FileNotFoundError("Face encodings not found. Run encode_faces.py first.")

        with open("models/encodings.pkl", "rb") as f:
            data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_names = data["names"]

    @staticmethod
    def mark_attendance(name):
        conn = sqlite3.connect("db/attendance.db")
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")

        c.execute("SELECT * FROM attendance WHERE name=? AND time LIKE ?", (name, today + '%'))
        already_marked = c.fetchone()

        if not already_marked:
            c.execute("INSERT INTO attendance (name, time) VALUES (?, ?)", (name, now))
            conn.commit()

        conn.close()

    def recognize(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding, box in zip(encodings, boxes):
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "Unknown"

            if True in matches:
                matchedIdx = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdx:
                    counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1

                name = max(counts, key=counts.get)
                self.mark_attendance(name)

            top, right, bottom, left = box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        return frame

    def get_names_only(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        recognized_names = []

        for encoding in encodings:
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                matchedIdx = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdx:
                    counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1
                name = max(counts, key=counts.get)

            if name != "Unknown":
                self.mark_attendance(name)
                recognized_names.append(name)

        return recognized_names
