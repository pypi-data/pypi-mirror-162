# System
import os
import datetime
import logging

# External
import numpy
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Locals
from .utils import data_split

def get_data(n_out,n_timestamp,record=None,verbose=False,n=4000,limit_low=0,limit_high=0.48,**kwargs):
    """
    https://stackoverflow.com/questions/36286566/how-to-generate-noisy-mock-time-series-or-signal-in-python
    """
    if record!=None and os.path.exists(os.path.expandvars(record)):
        dataset = numpy.loadtxt(record)
    else:
        dataset = numpy.random.normal(0, 0.5, n) \
                + numpy.abs(numpy.random.normal(0, 2, n) \
                            * numpy.sin(numpy.linspace(0, 3*numpy.pi, n)) ) \
                + numpy.sin(numpy.linspace(0, 5*numpy.pi, n))**2 \
                + numpy.sin(numpy.linspace(1, 6*numpy.pi, n))**2
        scaling = (limit_high - limit_low) / (max(dataset) - min(dataset))
        dataset = dataset * scaling
        dataset = dataset + (limit_low - min(dataset))
        if record!=None:
            numpy.savetxt(record,dataset,fmt='%f')
    if verbose:
        plt.style.use('seaborn')
        plt.figure(figsize=(6,4),dpi=200)
        plt.plot(dataset,lw=0.2)
        plt.axvline(0.6*n,ls='dashed',lw=1,color='black')
        plt.axvline(0.8*n,ls='dashed',lw=1,color='black')
        plt.tight_layout()
        plt.savefig('data.pdf')
    # Load and prepare data
    itrain = int(0.6*n)
    ivalid = int(0.2*n)
    # Set number of training, validation and testing sets
    training_set = dataset[:itrain].reshape(-1,1)
    validating_set = dataset[itrain: itrain+ivalid].reshape(-1,1)
    testing_set = dataset[itrain+ivalid:].reshape(-1,1)
    # Normalize data first
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    validating_set_scaled = sc.fit_transform(validating_set)
    testing_set_scaled = sc.fit_transform(testing_set)
    # Split data into n_timestamp
    train_set = data_split(training_set_scaled, n_timestamp, n_out, **kwargs)
    valid_set = data_split(validating_set_scaled, n_timestamp, n_out, **kwargs)
    test_set = data_split(testing_set_scaled, n_timestamp, n_out, step=n_out, **kwargs)
    return {'dataset':'fake',
            'train':train_set, 'valid':valid_set, 'test':test_set,
            'scaler':sc}
