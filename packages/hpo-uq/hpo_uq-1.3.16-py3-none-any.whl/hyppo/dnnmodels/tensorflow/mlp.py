# External
import tensorflow.keras as keras

# Local
from .utils import shape_and_size

def mlp_model(data=None, prms=None, **kwargs):
    prop = shape_and_size(data, **kwargs)
    model = keras.models.Sequential()
    model.add(
        keras.layers.Reshape(
            target_shape = (prop['input_size'],),
            input_shape  = prop['input_shape'],
        )
    )
    for ii in range(prms['layers']):
        if ii == 0:
            model.add(
                keras.layers.Dense(
                    units       = prms['nodes'][ii],
                    activation  = prms['activation'][ii],
                    input_shape = (prop['input_size'],)
                )
            )
        else:
            model.add(
                keras.layers.Dense(
                    units      = prms['nodes'][ii],
                    activation = prms['activation'][ii],
                )
            )
        if prms['dropout'][ii]!=0:
            model.add(
                keras.layers.Dropout(
                    rate = prms['dropout'][ii],
                )
            )
    model.add(
        keras.layers.Dense(
            units = prop['output_size']
        )
    )
    model.add(
        keras.layers.Reshape(
            target_shape = prop['output_shape'],
            input_shape  = (prop['output_size'],)
        )
    )
    return model

def get_model(**kwargs):
    """
    Constructs MLP model.
    """
    return mlp_model(**kwargs)
