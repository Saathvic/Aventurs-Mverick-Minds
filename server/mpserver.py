from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import tensorflow as tf
import threading
import pyttsx3

app = Flask(__name__)
CORS(app)

class_names = ["Angry", "Happy", "Sad", "Surprise"]
model = tf.keras.models.load_model("D:/Project/Hackathon now/mood prediction/model.h5")

engine = pyttsx3.init()
tts_lock = threading.Lock()

def detect_emotion(frame):
    emotion = model.predict(tf.expand_dims(frame, axis=0), verbose=0)[0]
    num = max(emotion)
    idx = list(emotion).index(num)
    return class_names[idx], num

def preprocess(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (48, 48))
    frame = frame / 255.0
    return frame

def detect_face(frame):
    cascade = cv2.CascadeClassifier('D:/Project/Hackathon now/mood prediction/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    face_coords = [(x, y, w, h) for (x, y, w, h) in faces]
    return gray, face_coords

def announce_moods(moods):
    with tts_lock:
        for mood in moods:
            engine.say(f"The detected mood is {mood}")
        engine.runAndWait()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    img_data = np.frombuffer(bytes(data['image']), np.uint8)
    frame = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    small_frame = cv2.resize(frame, (320, 240))
    gray, coordinates = detect_face(small_frame)
    
    detected_moods = []

    if coordinates:
        for face_coords in coordinates:
            x, y, w, h = face_coords
            gray_face = gray[y:y + h, x:x + w]
            processed_img = preprocess(gray_face)
            mood, confidence = detect_emotion(processed_img)
            detected_moods.append({"mood": mood, "confidence": float(confidence)})

    if detected_moods:
        threading.Thread(target=announce_moods, args=(detected_moods,)).start()

    return jsonify(detected_moods)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
