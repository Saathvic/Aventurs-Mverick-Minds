import os
import cv2
import pyttsx3
import time
from ultralytics import YOLO

CAMERA_ID = 0  # ID for the camera, usually 0 for the default camera

model = YOLO('model.pt')  # Load the YOLO model

class_ids = [489, 41, 160, 96, 567, 495, 549, 470, 553, 290, 264]  
threshold = 0.5  # Threshold for object detection confidence

cap = cv2.VideoCapture(CAMERA_ID)  # Open the camera

focal_length = 500  # Focal length of the camera in pixels
pixel_size = 0.001  # Size of a pixel in meters

# Initialize the TTS engine
engine = pyttsx3.init()

# Variable to keep track of the last announcement time
last_announcement_time = 0
announcement_interval = 15  # seconds

while True:
    ret, frame = cap.read()  # Read a frame from the camera

    if not ret:
        break

    results = model(frame)[0]  # Perform object detection on the frame

    print(f"Detected {len(results.boxes)} objects")

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        print(f"Object {class_id} with score {score:.2f}")

        if score > threshold and class_id in class_ids:
            print(f"Drawing box for object {class_id} with score {score:.2f}")
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cv2.putText(frame, results.names[class_id].upper(), (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

            # Calculate the distance of the object from the camera
            object_size_in_image = (x2 - x1) * (y2 - y1)
            real_object_size = 0.5  # Replace this with the actual size of the object in meters
            distance = (focal_length * real_object_size) / (object_size_in_image * pixel_size)
            distance_in_meters = distance / 10
            cv2.putText(frame, f"Distance: {distance_in_meters:.2f} m", (int(x1), int(y1 - 40)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

            # Announce the detected object and its distance if 15 seconds have passed
            current_time = time.time()
            if current_time - last_announcement_time > announcement_interval:
                announcement = f"Detected {results.names[class_id]} at a distance of {distance_in_meters:.2f} meters"
                engine.say(announcement)
                engine.runAndWait()
                last_announcement_time = current_time

    cv2.imshow('Object Detection', frame)  # Display the frame with object detection

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()  # Release the camera
cv2.destroyAllWindows()  # Close all windows
