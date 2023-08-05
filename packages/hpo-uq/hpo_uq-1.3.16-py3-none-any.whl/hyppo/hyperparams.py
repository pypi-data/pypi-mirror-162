# System
import os
import logging

# External
import pickle5 as pickle

# Local
from .dnnmodels import get_fct

def get_hyperprms(trainer, x_sc=None,record=None,library=None,**kwargs):
    """
    This function handles the recording and/or loading of the
    compelte hyperparameter set ready-to-use for training.
    
    Parameters
    ----------
    x_sc : :class:`dict`
      Dictionary of random hyperparameter values.
    record : :class:`bool`
      Path to pickle file to save/load the hyperparameter set.
      
    Returns
    -------
    hyperprms : :class:`dict`
      Complete hyperparameter set containing both the random
      values for the parameter to evaluate and the rest of the
      fixed parameters.
    """
    # Load custom hyperparameter set, if called and exist
    if record!=None and os.path.exists(os.path.expandvars(record)):
        filehandler = open(os.path.expandvars(record), 'rb')
        hyperprms = pickle.load(filehandler)
    else:
        # Dictionary with hyperparameter values
        if trainer=='internal':
            hyperprms = set_hyperparams(x_sc, library, **kwargs)
        else:
            hyperprms = x_sc
        if record!=None:
            filehandler = open(os.path.expandvars(record), 'wb')
            pickle.dump(hyperprms, filehandler)
    logging.info('-'*40)
    logging.info('Hyperparameters:')
    logging.info('-'*40 + '\n\n%s\n' % hyperprms)
    return hyperprms

def set_hyperparams(random_set, library, **kwargs):
    """
    This function merges into a single dictionary the hyperparameters
    that will be evaluated with the one that will be fixed. Pre-defined
    default values will be used for the fixed hyperparameters. The
    hardcoded default values can be changed by the user through the
    configuration file using the :ref:`default <change_default>` option.

    Parameters
    ----------
    random_set : :class:`dict`
      Random values for each hyperparameter to be evaluated
      
    Returns
    -------
    hpo_set : :class:`dict`
      Complete hyperparameter set
      
    Examples
    --------
    >>> from hyppo.hyperparams import set_hyperparams
    >>> set_hyperparams({'layers':3,'nodes':20},library='tf')
    {'activation': ['relu', 'relu', 'relu'],
     'batch': 8,
     'dropout': [0, 0, 0],
     'epochs': 10,
     'fc_activation': 'relu',
     'fc_dropout': 0,
     'fc_nodes': 10,
     'filter': [2, 2, 2],
     'kernel': [2, 2, 2],
     'lag': 0,
     'layers': 3,
     'loss': 'mean_squared_error',
     'loss_args': {},
     'maxpool': [0, 0, 0],
     'nodes': [20, 20, 20],
     'opt_args': {},
     'optimizer': 'Adam',
     'padding': ['valid', 'valid', 'valid'],
     'recurrent_activation': ['relu', 'relu', 'relu'],
     'recurrent_dropout': 0,
     'stride': 1}
    """
    # Specify the type for every hyperparameter
    params = {
        'activation':'relu',
        'batch':8,
        'dropout':0,
        'epochs':10,
        'factor':2,
        'fc_activation':'relu',
        'fc_dropout':0,
        'fc_nodes':10,
        'filter':2,
        'kernel':3,
        'lag':0,
        'layers':1,
        'lr':0.001,
        'loss':'mean_squared_error',
        'loss_args': {},
        'maxpool':2,
        'nodes':10,
        'optimizer':'Adam',
        'opt_args':{},
        'padding':'same',
        'recurrent_activation':'relu',
        'recurrent_dropout':0,
        'stride':1,
    }
    # Merge default and input values
    hpo_set = {**params, **random_set}
    # If existing, move random learning rate to relevant sub-dictionary
    hpo_set['opt_args']['lr'] = hpo_set['lr']
    del(hpo_set['lr'])
    # Available loss[0~13], optimizers[0~6] and activation[0~10] function in Keras
    activations = [
        'elu',
        'exponential',
        'hard_sigmoid',
        'linear',
        'relu',
        'selu',
        'sigmoid',
        'softmax',
        'softplus',
        'softsign',
        'tanh',
    ]
    losses = [
        'binary_crossentropy',
        'categorical_crossentropy',
        'categorical_hinge',
        'cosine_proximity',
        'hinge',
        'kullback_leibler_divergence',
        'logcosh',
        'mean_absolute_error',
        'mean_absolute_percentage_error',
        'mean_squared_error',
        'mean_squared_logarithmic_error',
        'poisson',
        'sparse_categorical_crossentropy',
        'squared_hinge',
    ]
    optimizers = [
        'Adadelta',
        'Adagrad',
        'Adam',
        'Adamax',
        'Nadam',
        'RMSprop',
        'sgd',
    ]
    paddings = ['valid', 'causal', 'same']
    # Check if input variable exists
    assert hpo_set['loss'] in losses, 'Loss function %s not available. Abort.'%hpo_set['loss']
    assert hpo_set['activation'] in activations, 'Activation function %s not available. Abort.'%hpo_set['activation']
    assert hpo_set['optimizer'] in optimizers, 'Activation function %s not available. Abort.'%hpo_set['optimizer']
    assert hpo_set['padding'] in paddings, 'Activation function %s not available. Abort.'%hpo_set['padding']
    # Use library function for categorical variables
    for key in ['activation','fc_activation','loss','optimizer','recurrent_activation']:
        hpo_set[key] = get_fct(library,category=key.split('_')[-1],fct=hpo_set[key])
    # Multiply some variables by number of layers
    for key in ['activation','dropout','nodes','filter','kernel','maxpool','padding','recurrent_activation','stride']:
        hpo_set[key] = hpo_set['layers']*[hpo_set[key]]
    return hpo_set

## Hyperparameters for optimizer
#* In the current code, we fix the optimizer. 
#* This function is for future updates when the optimizer is considered as tuning parameter

def hyp_opt(param):
    import tensorflow as tf
    tf_version= tf.__version__[0]
    if tf_version == str(1):
        import keras
    elif tf_version == str(2):
        import tensorflow.keras as keras
    """
        All Keras optimizers support the following keyword arguments:

        clipnorm: float >= 0. Gradients will be clipped when their L2 norm exceeds this value.
        clipvalue: float >= 0. Gradients will be clipped when their absolute value exceeds this value.
    """
    print("Optimizer", param['optimizer'], "setting")
    if param['optimizer'] == 'sgd':
        # default: keras.optimizers.SGD(lr=0.01, momentum=0.0, decay=0.0, nesterov=False)
        opt_param = {
            'lr': 0.01,         # float >= 0. Learning rate.
            'momentum': 0.0,    # float >= 0. Parameter that accelerates SGD in the relevant direction and dampens oscillations.
            'decay': 0.0,       # float >= 0. Learning rate decay over each update.
            'nesterov': False,  # boolean. Whether to apply Nesterov momentum.
            'clip': None,       # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.SGD(lr=opt_param['lr'],
                                       momentum=opt_param['momentum'], 
                                       decay=opt_param['decay'], 
                                       nesterov=opt_param['nesterov'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.SGD(lr=opt_param['lr'],
                                       momentum=opt_param['momentum'], 
                                       decay=opt_param['decay'], 
                                       nesterov=opt_param['nesterov'], 
                                       clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.SGD(lr=opt_param['lr'],
                                       momentum=opt_param['momentum'], 
                                       decay=opt_param['decay'], 
                                       nesterov=opt_param['nesterov'], 
                                       clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'RMSprop':
        # default: keras.optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0)
        opt_param = {
            'lr': 0.001,        # float >= 0. Learning rate.
            'rho': 0.9,         # float >= 0. 
            'epsilon': None,    # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'decay': 0.0,       # float >= 0. Learning rate decay over each update.
            'clip': None,       # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.RMSprop(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.RMSprop(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.RMSprop(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'Adagrad':
        # default: keras.optimizers.Adagrad(lr=0.01, epsilon=None, decay=0.0)
        opt_param = {
            'lr': 0.01,         # float >= 0. Learning rate.
            'epsilon': None,    # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'decay': 0.0,       # float >= 0. Learning rate decay over each update.
            'clip': None,       # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.Adagrad(lr=opt_param['lr'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.Adagrad(lr=opt_param['lr'],  
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.Adagrad(lr=opt_param['lr'],  
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'Adadelta':
        # default: keras.optimizers.Adadelta(lr=1.0, rho=0.95, epsilon=None, decay=0.0)
        opt_param = {
            'lr': 1.0,           # float >= 0. Learning rate.
            'rho': 0.95,         # float >= 0. Adadelta decay factor, corresponding to fraction of gradient to keep at each time step.
            'epsilon': None,     # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'decay': 0.0,        # float >= 0. Learning rate decay over each update.
            'clip': None,        # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.Adadelta(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.Adadelta(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.Adadelta(lr=opt_param['lr'], 
                                           rho=opt_param['rho'], 
                                           epsilon=opt_param['epsilon'], 
                                           decay=opt_param['decay'],
                                           clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'Adam':
        # default: keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        opt_param = {
            'lr': 0.001,           # float >= 0. Learning rate.
            'beta_1': 0.9,         # float, 0 < beta < 1. Generally close to 1.
            'beta_2': 0.999,       # float, 0 < beta < 1. Generally close to 1.
            'epsilon': None,       # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'decay': 0.0,          # float >= 0. Learning rate decay over each update.
            'amsgrad': False,      #  boolean. Whether to apply the AMSGrad variant of this algorithm from the paper "On the Convergence of Adam and Beyond".
            'clip': None,          # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.Adam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'],
                                        amsgrad=opt_param['amsgrad'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.Adam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'],
                                        amsgrad=opt_param['amsgrad'],
                                        clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.Adam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'],
                                        amsgrad=opt_param['amsgrad'],
                                        clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'Adamax':
        # default: keras.optimizers.Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)
        opt_param = {
            'lr': 0.002,           # float >= 0. Learning rate.
            'beta_1': 0.9,         # float, 0 < beta < 1. Generally close to 1.
            'beta_2': 0.999,       # float, 0 < beta < 1. Generally close to 1.
            'epsilon': None,       # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'decay': 0.0,          # float >= 0. Learning rate decay over each update.
            'clip': None,          # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.Adamax(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.Adamax(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'],
                                        clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.Adamax(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        decay=opt_param['decay'],
                                        clipvalue=opt_param['clipval'])
    elif param['optimizer'] == 'Nadam':
        # default: keras.optimizers.Nadam(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=None, schedule_decay=0.004)
        opt_param = {
            'lr': 0.002,             # float >= 0. Learning rate.
            'beta_1': 0.9,           # float, 0 < beta < 1. Generally close to 1.
            'beta_2': 0.999,         # float, 0 < beta < 1. Generally close to 1.
            'epsilon': None,         # float >= 0. Fuzz factor. If None, defaults to K.epsilon().
            'schedule_decay': 0.004, # floats, 0 < schedule_decay < 1.
            'clip': None,            # clip = None (will not set clip) or 'clipnorm' or 'clipvalue'
            'clipval': 1.0,
        }
        if opt_param['clip'] == None:
            opt = keras.optimizers.Nadam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        schedule_decay=opt_param['schedule_decay'])
        elif opt_param['clip'] == 'clipnorm':
            opt = keras.optimizers.Nadam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        schedule_decay=opt_param['schedule_decay'],
                                        clipnorm=opt_param['clipval'])
        elif opt_param['clip'][0] == 'clipvalue':
            opt = keras.optimizers.Nadam(lr=opt_param['lr'], 
                                        beta_1=opt_param['beta_1'], 
                                        beta_2=opt_param['beta_2'], 
                                        epsilon=opt_param['epsilon'], 
                                        schedule_decay=opt_param['schedule_decay'],
                                        clipvalue=opt_param['clipval'])
    print(opt_param)
    return(opt_param, opt)
