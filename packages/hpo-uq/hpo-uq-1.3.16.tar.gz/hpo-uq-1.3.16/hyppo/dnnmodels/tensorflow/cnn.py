# External
import tensorflow.keras as keras

# Local
from .utils import shape_and_size

def cnn_model(data=None, prms=None, **kwargs):
    prop = shape_and_size(data, **kwargs)
    model = keras.models.Sequential()
    for ii in range(prms['layers']):
        if ii == 0:
            model.add(
                keras.layers.Conv2D(
                    filters     = prop['input_shape'][-1]*prms['factor']**(ii+1), 
                    kernel_size = prms['kernel'][ii],
                    padding     = prms['padding'][ii],
                    strides     = prms['stride'][ii],
                    activation  = prms['activation'][ii],
                    input_shape = prop['input_shape'],
                )
            )
        else:
            model.add(
                keras.layers.Conv2D(
                    filters     = prop['input_shape'][-1]*prms['factor']**(ii+1), 
                    kernel_size = prms['kernel'][ii],
                    padding     = prms['padding'][ii],
                    strides     = prms['stride'][ii],
                    activation  = prms['activation'][ii],
                )
            )
        if prms['maxpool'][ii]!=0:
            model.add(
                keras.layers.MaxPooling2D(
                    pool_size = prms['maxpool'][ii],
                )
            )
        if prms['dropout'][ii]!=0:
            model.add(
                keras.layers.Dropout(
                    rate = prms['dropout'][ii],
                )
            )

    # flatten
    model.add(
        keras.layers.Flatten()
    )
    model.add(
        keras.layers.Dense(
            units      = prms['fc_nodes'],
            activation = prms['fc_activation'],
        )
    )
    if prms['fc_dropout']!=0:
        model.add(
            keras.layers.Dropout(
                rate = prms['fc_dropout'],
            )
        )
    # output
    model.add(
        keras.layers.Dense(prop['output_size'])
    )
    model.add(
        keras.layers.Reshape(
            target_shape = prop['output_shape'],
            input_shape = (prop['output_size'],),
        )
    )
    return model


def get_model(**kwargs):
    """
    Constructs CNN model.
    """
    return cnn_model(**kwargs)
