# System
import os
import logging
from urllib.request import urlopen
from shutil import copyfileobj

# External
from pandas import read_csv
#import pickle5 as pickle
from sklearn.preprocessing import MinMaxScaler

# Locals
from .plots import show_acf
from .utils import data_split

def get_data(n_out, n_timestamp, data_path='./', verbose=False, **kwargs):
    logging.info('='*40)
    logging.info('DATASET:')
    logging.info('-'*40)
    if data_path=='temperature':
        # data_path = 'daily-min-temperatures.pickle' 
        data_path = 'daily-min-temperatures.csv'
        if os.path.exists(data_path)==False:
            logging.info('\tDownloading dataset...')
            url_path = 'https://gitlab.com/hpo-uq/hyppo/-/raw/master/data/temperature/'+data_path
            with urlopen(url_path) as in_stream, open(data_path, 'wb') as out_file:
                copyfileobj(in_stream, out_file)
    assert os.path.exists(os.path.expandvars(data_path)), 'Dataset at %s does not exist. Abort.' % data_path
    logging.info('\tLoading dataset...')
    while True:
        try:
            dataset = read_csv(os.path.expandvars(data_path), header=0, index_col=0, engine='python')
            break
        except:
            pass
    logging.info('\tSize of dataset: %i' % len(dataset))
    if verbose:
        show_acf(dataset)
    # Load and prepare data
    itrain = int(0.6*len(dataset))
    ivalid = int(0.2*len(dataset))
    # Set number of training and testing data
    train_data = dataset[:itrain].reset_index(drop=True)
    valid_data = dataset[itrain: itrain+ivalid].reset_index(drop=True)
    test_data = dataset[itrain+ivalid:].reset_index(drop=True)
    # Preparing training sets
    training_set = train_data.iloc[:].values
    validating_set = valid_data.iloc[:].values
    testing_set = test_data.iloc[:].values
    # Normalize data first
    logging.info('\tTransform dataset...')
    sc = MinMaxScaler(feature_range = (0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    validating_set_scaled = sc.fit_transform(validating_set)
    testing_set_scaled = sc.fit_transform(testing_set)
    # Split data into n_timestamp
    train_set = data_split(training_set_scaled, n_timestamp, n_out, **kwargs)
    valid_set = data_split(validating_set_scaled, n_timestamp, n_out, **kwargs)
    test_set = data_split(testing_set_scaled, n_timestamp, n_out, step=n_out, **kwargs)
    logging.info('\tData preparation completed!')
    logging.info('='*40+'\n')
    return {'dataset':'generic',
            'train':train_set, 'valid':valid_set, 'test':test_set,
            'scaler':sc}
