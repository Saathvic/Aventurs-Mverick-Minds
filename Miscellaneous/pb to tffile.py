import tensorflow as tf

# Load the .h5 model
h5_model_path = 'model.h5'
model = tf.keras.models.load_model(h5_model_path)

# Define the directory where the SavedModel will be saved
saved_model_dir = 'D:/Project/Hackathon 1/MOOD DETECTION'

# Export the model to the SavedModel format (TensorFlow format)
model.export(saved_model_dir)
