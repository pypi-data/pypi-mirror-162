# Author: Viraj Khanna <viraj@virajkhanna.in>
# Copyright © Viraj Khanna 2022

import tensorflow as tf
import numpy as np
import os
from os.path import expanduser

def classify_number(image_url):

  home = expanduser("~")

  model = tf.keras.models.load_model(".\\ai-models\\num-predict.h5")

  def get_image_from_url(image_url):
    if os.path.exists(home + '\.keras\datasets\test_image.jpg'):
      os.remove(home + '\.keras\datasets\test_image.jpg')

    image_path = tf.keras.utils.get_file('test_image.jpg', origin=image_url)
    return image_path
  
  image_path = get_image_from_url(image_url)
  
  image = tf.keras.preprocessing.image.load_img(image_path, target_size=(28,28)).convert('L')

  plt.figure()
  plt.imshow(image, cmap='gray')

  image = tf.keras.preprocessing.image.img_to_array(image)
  image = np.expand_dims(image, axis=0)
  prediction_result = model.predict(image, batch_size=1)
  return prediction_result.argmax()

