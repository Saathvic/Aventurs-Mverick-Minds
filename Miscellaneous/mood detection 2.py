import cv2
import tensorflow as tf
import threading
import time

class_names = ["Angry", "Happy", "Sad", "Surprise"]

def load_model():
    # Load the TensorFlow model once to avoid reloading it for each frame
    return tf.keras.models.load_model("model.h5")

def detect_emotion(model, frame):
    # Predict the emotion from the preprocessed frame
    emotion = model.predict(tf.expand_dims(frame, axis=0))
    emotion = emotion[0]  # Get the first prediction
    num = max(emotion)
    idx = list(emotion).index(num)
    return idx, num

def preprocess(frame):
    # Convert the frame to RGB, resize to 48x48, and normalize
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (48, 48))
    frame = frame / 255.0
    return frame

def process_frame(model, frame):
    # Use Haar Cascade to detect faces in the frame
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face_img = gray[y:y + h, x:x + w]
        processed_img = preprocess(face_img)
        idx, conf = detect_emotion(model, processed_img)
        
        if conf > 0.3:
            class_name = class_names[idx]
            cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
    
    cv2.imshow("Emotion Detection", frame)

def video_stream():
    model = load_model()
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if ret:
            process_frame(model, frame)
            cv2.waitKey(1)
            time.sleep(2)  # Introduce a 2-second delay

    video.release()
    cv2.destroyAllWindows()

# Start the video stream in a separate thread
video_thread = threading.Thread(target=video_stream)
video_thread.start()
