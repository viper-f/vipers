import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model('model-2024-03-24.keras')
prediction = model.predict(np.array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0]))
print(prediction)