from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import pyttsx3
import time
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

model = YOLO('model.pt')  # Load the YOLO model

class_ids = [489, 41, 160, 96, 567, 495, 549, 470, 553, 290, 264]
threshold = 0.5  # Threshold for object detection confidence
focal_length = 500  # Focal length of the camera in pixels
pixel_size = 0.001  # Size of a pixel in meters

# Initialize the TTS engine
engine = pyttsx3.init()

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return "No image file provided", 400

    image_file = request.files['image']
    image = np.frombuffer(image_file.read(), np.uint8)
    frame = cv2.imdecode(image, cv2.IMREAD_COLOR)

    results = model(frame)[0]  # Perform object detection on the frame

    detected_objects = []
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > threshold and class_id in class_ids:
            object_info = {
                'class_id': class_id,
                'class_name': results.names[class_id],
                'score': score,
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }

            # Calculate the distance of the object from the camera
            object_size_in_image = (x2 - x1) * (y2 - y1)
            real_object_size = 0.5  # Replace this with the actual size of the object in meters
            distance = (focal_length * real_object_size) / (object_size_in_image * pixel_size)
            distance_in_meters = distance / 10
            object_info['distance'] = distance_in_meters

            detected_objects.append(object_info)

    response = jsonify(detected_objects)
    response.status_code = 200
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
