import tensorflow as tf

# Convert the model
converter = tf.lite.TFLiteConverter.from_saved_model('D:/Project/Hackathon now/Obj det') # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('model2.tflite', 'wb') as f:
  f.write(tflite_model)