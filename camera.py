# app/camera.py
import cv2
from app.recognizer import Recognizer

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.recognizer = Recognizer()

    def __del__(self):
        self.video.release()

    def get_frames(self):
        success, frame = self.video.read()
        if not success:
            return b""

        frame = self.recognizer.recognize(frame)  # Call class method

        _, buffer = cv2.imencode('.jpg', frame)
        return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'

