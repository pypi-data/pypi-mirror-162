# Made by VIRAJ KHANNA <viraj@virajkhanna.in>
# Copyright © Viraj Khanna 2022

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
from os.path import expanduser

def classify_object(url):

  home = expanduser("~")

  model = tf.keras.applications.EfficientNetB7()

  def get_image_from_url(image_url):
    if os.path.exists(home + '//.keras//datasets//test_image.jpg'):
      os.remove(home + '//.keras//datasets//test_image.jpg')

    image_path = tf.keras.utils.get_file('test_image.jpg', origin=image_url)
    return image_path

  def print_classifications(classifications):
      for (classification, number) in zip(classifications[0], range(1, len(classifications[0])+1)):
        print('{}'.format(classification[1]))
  
  image_path = get_image_from_url(url)
  image = tf.keras.preprocessing.image.load_img(image_path, target_size=(600, 600))

  plt.figure()
  plt.imshow(image)

  image = tf.keras.preprocessing.image.img_to_array(image)
  image = np.expand_dims(image, axis=0)

  classification_result = model.predict(image, batch_size=1)

  classifications = tf.keras.applications.imagenet_utils.decode_predictions(classification_result, top=1)

  return print_classifications(classifications)
