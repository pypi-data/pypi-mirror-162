# System
import copy
from collections import OrderedDict

# External
import torch
import numpy

def shape_and_size(data, n_classes=None, **kwargs):
    """
    Extract input/output shape and size. This function is used to determine
    the right dimension of both input and output data.
    
    Parameters
    ----------
    data : :py:class:`dict`
      Dictionary containing both input data (X_data key) and output labels (y_data key).
    n_classes : :py:class:`int`
      Number of output classes. Must be used when classification datasets are used.
    
    Returns
    -------
    prop : :py:class:`dict`
      Input/output shape and size dimensions.
    """
    # Get input and output datasets
    X_data, y_data = next(iter(data))
    # Extract input/output size and shapes
    prop = {}
    prop['input_shape'] = X_data.shape[1:]
    prop['input_size'] = numpy.prod(prop['input_shape'])
    prop['output_shape'] = y_data.shape[1:] if n_classes==None else torch.Size([n_classes])
    prop['output_size'] = numpy.prod(prop['output_shape'])
    return prop

def get_fct(category,fct=None):
    """
    Load PyTorch function of target element.
    
    Parameters
    ----------
    category : :py:class:`str`
      Target type of function to lookup in PyTorch (i.e. activation, loss, or optimizer function).
    fct : :py:class:`str`
      Target function to lookup with the above category.
    """
    pytorch_dict = {
        # Activation functions,
        'activation':{
            'elu': torch.nn.ELU,
            'exponential': None,
            'hard_sigmoid': torch.nn.Hardsigmoid,
            'linear': torch.nn.Linear,
            'relu': torch.nn.ReLU,
            'selu': torch.nn.SELU,
            'sigmoid': torch.nn.Sigmoid,
            'softmax': torch.nn.Softmax,
            'softplus': torch.nn.Softplus,
            'softsign': torch.nn.Softsign,
            'tanh': torch.nn.Tanh,
        },
        # Loss functions
        'loss':{
            'binary_crossentropy': torch.nn.BCELoss,
            'categorical_crossentropy': torch.nn.CrossEntropyLoss,
            'categorical_hinge': None,
            'cosine_proximity': None,
            'hinge': None,
            'kullback_leibler_divergence': torch.nn.KLDivLoss,
            'logcosh': None,
            'mean_absolute_error': torch.nn.L1Loss,
            'mean_absolute_percentage_error': None, 
            'mean_squared_error': torch.nn.MSELoss,
            'mean_squared_logarithmic_error': None,
            'poisson': None,
            'squared_hinge': None, 
        },
        # Optimizer functions
        'optimizer':{
            'Adadelta': torch.optim.Adadelta,
            'Adagrad': torch.optim.Adagrad,
            'Adam': torch.optim.Adam,
            'Adamax': torch.optim.Adamax,
            'Nadam': None,
            'RMSprop': torch.optim.RMSprop,
            'sgd': torch.optim.SGD,
        }
    }
    return pytorch_dict[category] if fct==None else pytorch_dict[category][fct]

def load_model(fname,model,device='cpu'):
    """
    Load saved model's parameter dictionary to initialized model.
    The function will remove any ``.module`` string from parameter's name.

    Parameters
    ----------
    fname : :py:class:`str`
      Path to saved model
    model : :py:class:`torch.nn.Module`
      Initialized network network architecture
    device : :py:class:`str`
      Type of processor used (CPU or GPU'

    Returns
    -------
    model : :py:class:`torch.nn.Module`
      Up-to-date neural network model
    """
    model = copy.deepcopy(model)
    state_dict = torch.load(fname, map_location=device)
    new_state_dict = OrderedDict()
    for key, value in state_dict.items():
        if key.startswith('module.'):
            key = key[7:]
        new_state_dict[key] = value
    model.load_state_dict(new_state_dict)
    return model

