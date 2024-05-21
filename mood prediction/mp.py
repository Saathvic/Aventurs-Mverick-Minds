import cv2
import tensorflow as tf
import pyttsx3
import threading
import time

class_names = ["Angry", "Happy", "Sad", "Surprise"]
model = tf.keras.models.load_model("D:/Project/Hackathon now/mood prediction/model.h5")

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Create a lock for the text-to-speech engine
tts_lock = threading.Lock()

# Initialize the last prediction time
last_prediction_time = time.time()

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

    face_coords = []
    for (x, y, w, h) in faces:
        face_coords.append((x, y, w, h))
    return gray, face_coords

def announce_moods(moods):
    with tts_lock:
        for mood in moods:
            engine.say(f"The detected mood is {mood}")
        engine.runAndWait()

def process_frame(frame):
    global last_prediction_time

    current_time = time.time()
    if current_time - last_prediction_time < 6:
        return

    small_frame = cv2.resize(frame, (320, 240))
    gray, coordinates = detect_face(small_frame)

    detected_moods = []  # List to store detected moods

    if coordinates:
        for face_coords in coordinates:
            x, y, w, h = face_coords
            gray_face = gray[y:y + h, x:x + w]
            processed_img = preprocess(gray_face)
            mood, confidence = detect_emotion(processed_img)
            detected_moods.append(mood)  # Add detected mood to the list
            print(f"Detected mood: {mood}, Confidence: {confidence}")

    if detected_moods:
        # Announce all detected moods
        announcement_thread = threading.Thread(target=announce_moods, args=(detected_moods,))
        announcement_thread.start()

    last_prediction_time = current_time

def video_stream():
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()

        if ret:
            process_frame(frame)
            
            # Display the frame in a window
            cv2.imshow('Video Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    video.release()
    cv2.destroyAllWindows()

video_stream()