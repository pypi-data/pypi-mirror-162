# System
import os
import datetime

# External
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler

# Locals
from .plots import *
from .utils import data_split

def get_data(data_path,link,n_out,n_timestamp,verbose=False,**kwargs):
    if type(link)==int:
        link-=1
    # Load and prepare Mariam's data
    train_days = 24*200  # Number of days to train from
    valid_days = 24*100  # Number of days to validate from
    testing_days = 24*365-train_days-valid_days # Number of days to be predicted
    filter_on = 1
    # prep transatlantic data
    def parse(x):
    	return datetime.datetime.strptime(x, '%d/%m/%Y %H:%M')
    dataset = read_csv(os.path.expandvars(data_path))
    links = dataset.columns.values[1:]
    if verbose:
        show_raw_visualization(dataset,links)
    # Load dataset
    dataset = read_csv(os.path.expandvars(data_path), header=0, index_col=0)
    # Heatmap to show feature correlations
    if verbose:
        show_data(dataset)
        show_heatmap(dataset)
    # Set number of training and testing data
    train_data = dataset[:train_days].reset_index(drop=True)
    valid_data = dataset[train_days: train_days+valid_days].reset_index(drop=True)
    test_data = dataset[train_days+valid_days:].reset_index(drop=True)
    scs, train_set, valid_set, test_set = [], None, None, None
    for i in range(len(links)):
        if link in [i,'all']:
            training_set = train_data.iloc[:, i:i+1].values
            validating_set = valid_data.iloc[:, i:i+1].values
            testing_set = test_data.iloc[:, i:i+1].values
            # Normalize data first
            sc = MinMaxScaler(feature_range = (0, 1))
            training_set_scaled = sc.fit_transform(training_set)
            validating_set_scaled = sc.fit_transform(validating_set)
            testing_set_scaled = sc.fit_transform(testing_set)
            # Split data into n_timestamp
            training_set = data_split(training_set_scaled, n_timestamp, n_out, **kwargs)
            validating_set = data_split(validating_set_scaled, n_timestamp, n_out, **kwargs)
            testing_set = data_split(testing_set_scaled, n_timestamp, n_out, step=n_out, **kwargs)
            # Concatenate to existing dictionary
            if train_set==None:
                train_set = training_set
                valid_set = validating_set
                test_set = testing_set
            else:
                for key in ['X_data','y_data']:
                    train_set[key] = numpy.hstack((train_set[key],training_set[key]))
                    valid_set[key] = numpy.hstack((valid_set[key],validating_set[key]))
                    test_set[key] = numpy.hstack((test_set[key],testing_set[key]))
            scs.append(sc)
    return {'dataset':'network',
            'train':train_set,
            'valid':valid_set,
            'test':test_set,
            'links':links,
            'link':link,
            'scaler':scs}
