# System
import os
import glob
import random

# External
import numpy

def get_data(library=None,data_path='./data',**kwargs):
    """
    Loading `CIFAR10 dataset <https://www.cs.toronto.edu/~kriz/cifar.html>`_.
    This image dataset consists of 60,000 32x32 colour images across 10 classes
    and can be used to test image classification problems. Depending on which
    library is being used, this function will load the public dataset accordingly.
    
    Parameters
    ----------
    library : :class:`str`
      Machine Learning Library
    data_path : :class:`str`
      Path to data repository
      
    Returns
    -------
    data : :class:`dict`
      Training, validation and testing datasets.
      
    Examples
    --------
    >>> from hyppo.dataset.cifar10 import get_data
    >>> get_data(library='pt')
    {'dataset': 'cifar10',
     'train': <torch.utils.data.dataset.Subset at 0x11deb3090>,
     'valid': <torch.utils.data.dataset.Subset at 0x11deb3fd0>,
     'test': Dataset CIFAR10
         Number of datapoints: 10000
         Root location: ./data
         Split: Test
         StandardTransform
     Transform: Compose(
                    ToTensor()
                )}
    """
    if library=='pt':
        import torchvision
        import torchvision.transforms as transforms
        from torch.utils.data import DataLoader, random_split
        transform = transforms.Compose([transforms.ToTensor()])
        train_set = torchvision.datasets.CIFAR10(root=data_path, train=True, download=True, transform=transform)
        train_set, valid_set = random_split(train_set,[42000,8000])
        test_set = torchvision.datasets.CIFAR10(root=data_path, train=False, download=True, transform=transform)
    elif library=='tf':
        import tensorflow as tf
        (X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()
        (X_valid, y_valid) = X_train[42000:].astype('float32')/255., y_train[42000:]
        (X_train, y_train) = X_train[:42000].astype('float32')/255., y_train[:42000]
        X_test = X_test.astype('float32')/255.
        train_set = {'X_data':X_train, 'y_data':y_train}
        valid_set = {'X_data':X_valid, 'y_data':y_valid}
        test_set  = {'X_data':X_test,  'y_data':y_test}
    data = {'train':train_set, 'valid':valid_set, 'test':test_set}
    return data
