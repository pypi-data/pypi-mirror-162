from keras.models import Model
from keras.layers import Activation, BatchNormalization, Add, Reshape, DepthwiseConv2D
from keras.utils.vis_utils import plot_model
import efficientnet.keras as enet
from keras import backend as K
from keras.backend import sigmoid
from keras.layers import Dense, Dropout, Activation, BatchNormalization, Flatten
from keras.utils.generic_utils import get_custom_objects

class SwishActivation(Activation):

    def __init__(self, activation, **kwargs):
        super(SwishActivation, self).__init__(activation, **kwargs)
        self.__name__ = 'swish_act'


def swish_act(x, beta=1):
    return x * sigmoid(beta * x)

get_custom_objects().update({'swish_act': SwishActivation(swish_act)})

def EfficientNet_Custom(input_shape, num_classes):
    """EfficientNet custom dataset

    # Arguments
        input_shape: An integer or tuple/list of 3 integers, shape
            of input tensor.
        num_class: Integer, number of classes.


    # Returns
        model.
    """
    model = enet.EfficientNetB3(include_top=False, input_shape=input_shape, pooling='avg', weights='imagenet')

    model.trainable = False

    # building 2 fully connected layer
    x = model.output

    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    x = Dense(512)(x)
    x = BatchNormalization()(x)
    x = Activation(swish_act)(x)
    x = Dropout(0.5)(x)

    x = Dense(128)(x)
    x = BatchNormalization()(x)
    x = Activation(swish_act)(x)

    # output layer
    predictions = Dense(num_classes, activation="softmax")(x)

    model_final = Model(inputs=model.input, outputs=predictions)

    return model_final


if __name__ == '__main__':
    model = EfficientNet_Custom((224, 224, 3), 2)
    print(model.summary())
