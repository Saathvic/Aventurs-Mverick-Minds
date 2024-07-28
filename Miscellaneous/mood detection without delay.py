import cv2
import tensorflow as tf
import threading

class_names = ["Angry", "Happy", "Sad", "Surprise"]

def detect_emotion(frame):
    model = tf.keras.models.load_model("model.h5")
    emotion = list(model.predict(tf.expand_dims(frame, axis=0)))
    num = max(emotion[0])
    idx = list(emotion[0]).index(num)
    return idx, num

def preprocess(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (48, 48))
    frame = frame / 255.
    return frame

def detect_face(frame):
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return gray, frame, faces

def process_frame(frame):
    gray, frame, coordinates = detect_face(frame)
    if coordinates is not None and len(coordinates) > 0:
        x, y, w, h = coordinates[0]
        gray = gray[y:y + h, x:x + w]
        process_img = preprocess(gray)
        idx, conf = detect_emotion(process_img)
        class_name = class_names[idx]
        if conf > 0.3:
            cv2.putText(frame, class_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
    cv2.imshow("Window", frame)

def video_stream():
    video = cv2.VideoCapture(0)
    while True:
        ret, frame = video.read()
        if ret:
            process_frame(frame)
            cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()

# Start the video stream in a separate thread
video_thread = threading.Thread(target=video_stream)
video_thread.start()
