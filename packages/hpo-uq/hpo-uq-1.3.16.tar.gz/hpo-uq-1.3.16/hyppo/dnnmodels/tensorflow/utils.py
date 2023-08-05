# System
import os
import logging

# External
import numpy
import tensorflow.keras as keras

def shape_and_size(data, n_classes=None, **kwargs):
    # Get input and output datasets
    X_data, y_data = data['X_data'], data['y_data']
    # Extract input/output size and shapes
    prop = {}
    prop['input_shape'] = X_data.shape[1:]
    prop['input_size'] = numpy.prod(prop['input_shape'])
    prop['output_shape'] = y_data.shape[1:] if n_classes==None else [n_classes]
    prop['output_size'] = numpy.prod(prop['output_shape'])
    return prop

def get_callbacks(epochs,output_dir='out',save_model=False,**kwargs):
    callbacks = [LossPrinting(epochs)]
    if save_model:
        checkpoint_dir = os.path.join('checkpoints',output_dir)
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir,'model_checkpoint_{epoch:03d}.hdf5')
        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path)
        callbacks.append(cp_callback)
    return callbacks

class LossPrinting(keras.callbacks.Callback):
    def __init__(self,epochs):
        self.epochs = epochs
    def on_epoch_end(self, epoch, logs=None):
        log = '\tEpoch {:>3}/{:<3} | Training Loss {:>11.5f}'.format(epoch+1,self.epochs,logs['loss'])
        if 'accuracy' in logs.keys():
            log += ' | Training Accuracy {:>7.2f} %'.format(100*logs['accuracy'])
        if 'val_loss' in logs.keys():
            log += ' | Validation Loss {:>11.5f}'.format(logs['val_loss'])
        if 'val_accuracy' in logs.keys():
            log += ' | Validation Accuracy {:>7.2f} %'.format(100*logs['val_accuracy'])
        logging.info(log)

def get_fct(category,fct=None):
    pytorch_dict = {
        # Activation functions,
        'activation':{
            'elu': keras.activations.elu,
            'exponential': keras.activations.exponential,
            'hard_sigmoid': keras.activations.hard_sigmoid,
            'linear': keras.activations.linear,
            'relu': keras.activations.relu,
            'selu': keras.activations.selu,
            'sigmoid': keras.activations.sigmoid,
            'softmax': keras.activations.softmax,
            'softplus': keras.activations.softplus,
            'softsign': keras.activations.softsign,
            'tanh': keras.activations.tanh,
        },
        # Loss functions
        'loss':{
            'binary_crossentropy': keras.losses.BinaryCrossentropy,
            'categorical_crossentropy': keras.losses.CategoricalCrossentropy,
            'categorical_hinge': keras.losses.CategoricalHinge,
            'cosine_proximity': keras.losses.cosine_similarity,
            'hinge': keras.losses.Hinge,
            'kullback_leibler_divergence': keras.losses.KLDivergence,
            'logcosh': keras.losses.log_cosh,
            'mean_absolute_error': keras.losses.MeanAbsoluteError,
            'mean_absolute_percentage_error': keras.losses.MeanAbsolutePercentageError, 
            'mean_squared_error': keras.losses.MeanSquaredError,
            'mean_squared_logarithmic_error': keras.losses.MeanSquaredLogarithmicError,
            'poisson': keras.losses.Poisson,
            'sparse_categorical_crossentropy': keras.losses.SparseCategoricalCrossentropy,
            'squared_hinge': keras.losses.SquaredHinge, 
        },
        # Optimizer functions
        'optimizer':{
            'Adadelta': keras.optimizers.Adadelta,
            'Adagrad': keras.optimizers.Adagrad,
            'Adam': keras.optimizers.Adam,
            'Adamax': keras.optimizers.Adamax,
            'Nadam': keras.optimizers.Nadam,
            'RMSprop': keras.optimizers.RMSprop,
            'sgd': keras.optimizers.SGD,
        }
    }
    return pytorch_dict[category] if fct==None else pytorch_dict[category][fct]
