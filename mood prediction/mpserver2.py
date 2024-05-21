from flask import Flask, request, jsonify
import cv2
import tensorflow as tf
import numpy as np

app = Flask(__name__)

class_names = ["Angry", "Happy", "Sad", "Surprise"]
model = tf.keras.models.load_model("model.h5")

def preprocess(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (48, 48))
    frame = frame / 255.0
    return frame

def detect_emotion(frame):
    emotion = model.predict(tf.expand_dims(frame, axis=0), verbose=0)[0]
    num = max(emotion)
    idx = list(emotion).index(num)
    return class_names[idx], num

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    file_bytes = np.fromstring(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return jsonify({"error": "No face detected"}), 400

    x, y, w, h = faces[0]
    gray_face = gray[y:y + h, x:x + w]
    processed_img = preprocess(gray_face)
    mood, confidence = detect_emotion(processed_img)
    return jsonify({"mood": mood, "confidence": confidence})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
