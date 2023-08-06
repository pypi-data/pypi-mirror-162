import shutil
import time
import numpy as np
from tensorflow import nn
from tensorflow.keras.layers import Dropout, Activation
import os
import cv2
from tensorflow.keras.models import load_model
from keras.backend import sigmoid
from tensorflow.keras.backend import shape


class FixedDropout(Dropout):
    def _get_noise_shape(self, inputs):
        if self.noise_shape is None:
            return self.noise_shape
        return tuple([shape(inputs)[i] if sh is None else sh for i, sh in enumerate(self.noise_shape)])


class SwishActivation(Activation):
    def __init__(self, activation, **kwargs):
        super(SwishActivation, self).__init__(activation, **kwargs)
        self.__name__ = 'swish_act'


def swish_act(x, beta=1):
    return x * sigmoid(beta * x)


customObjects = {
    'swish_act': SwishActivation(swish_act),
    'swish': nn.swish,
    'FixedDropout': FixedDropout
}


def predict(model, img):
    x = cv2.resize(img, (300, 300))
    x = np.expand_dims(x, axis=0)
    x = x / 255.0

    pred = model.predict(x)
    pred_classes = np.argmax(pred)
    return pred_classes, pred[0][pred_classes]


def find_img_contain_text(model_path, folder_input, folder_output):
    time_start = time.perf_counter()
    if os.path.isdir(folder_output):
        shutil.rmtree(folder_output)
    os.mkdir(folder_output)
    model = load_model(model_path, custom_objects=customObjects)
    for file_name in os.listdir(folder_input):
        full_file_name = os.path.join(folder_input, file_name)
        img = cv2.imread(full_file_name)
        result = predict(model, img)
        if (result[0] == 1):
            shutil.copy(full_file_name, folder_output)
    time_process = time.perf_counter() - time_start
    print(f'Time classify: {time_process}')
    return time_process

# from joblib import Parallel, delayed
# def move_file(path_img, model, folder_output):
#     img = cv2.imread(path_img)
#     result = predict(model, img)
#     if (result[0] == 1):
#         shutil.move(path_img, folder_output)
# def find_img_contain_text_parallel(model_path, folder_input, folder_output):
#     time_start = time.perf_counter()
#     if os.path.isdir(folder_output):
#         shutil.rmtree(folder_output)
#     os.mkdir(folder_output)
#     model = load_model(model_path, custom_objects=customObjects)
#     Parallel(n_jobs=6)(delayed(move_file)(os.path.join(folder_input, file_name), model, folder_output) for file_name in
#                        os.listdir(folder_input))
#
#     time_process = time.perf_counter() - time_start
#     print(f'Time classify: {time_process}')
#     return time_process
