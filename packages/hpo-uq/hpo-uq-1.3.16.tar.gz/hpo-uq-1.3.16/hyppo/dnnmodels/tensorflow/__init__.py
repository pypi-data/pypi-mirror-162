# System
import logging
import time
import importlib

# External
import numpy
import tensorflow.keras as keras

#local
from .utils import get_callbacks

def train(itrial     = 0,
          data       = None,
          hyperprms  = None,
          dl_type    = None,
          output     = None,
          debug      = False,
          trial      = 1,
          validate   = True,
          accuracy   = False,
          device     = None,
          device_ids = None,
          log_dir    = 'logs',
          split      = 'data',
          ntasks     = 1,
          rank       = 0,
          **kwargs):

    """
    TensorFlow training method.
    """
    loss_function = hyperprms['loss'](**hyperprms['loss_args'])
    test_loss = []
    for i in range(trial):
        if trial>1:
            logging.info('\tTRIAL {:>3}/{:<3}'.format(i+1,trial))    
        # Architecture initialization
        module = importlib.import_module('.' + dl_type.lower(), 'hyppo.dnnmodels.tensorflow')
        model = module.get_model(data=data['train'], prms=hyperprms, **kwargs)
        # Check if debugging mode (summary display) requested
        if debug==1:
            print(model.summary())
            quit()
        # Compile model with loss function and optimizer
        model.compile(
            loss      = loss_function,
            optimizer = hyperprms['optimizer'](**hyperprms['opt_args']),
            metrics   = ['accuracy'] if accuracy else None,
        )
        # Train single trial
        t0 = time.time()
        model.fit(
            data['train']['X_data'],
            data['train']['y_data'],
            verbose         = 0,
            batch_size      = hyperprms['batch'],
            epochs          = 1 if debug==2 else hyperprms['epochs'],
            validation_data = (data['valid']['X_data'],data['valid']['y_data']) if validate else None,
            callbacks       = get_callbacks(hyperprms['epochs'], **kwargs),
            shuffle         = True,
        )
        t1 = time.time()-t0
        # Evaluate trained model with test dataset
        trial_loss, trial_acc = evaluate(data['test'], model, loss_function, **kwargs)
        test_loss.append(trial_loss)
        log = '{:>32} {:>11.5f}'.format('| Testing  Loss',trial_loss)
        if accuracy:
            log += ' | Testing  Accuracy {:>7.2f} %'.format(trial_acc)
        logging.info(log)
        t2 = time.time()-t1-t0
        # Print execution times
        logging.info('{:>16} : {:>12.5f} s'.format('Train Time',t1))
        logging.info('{:>16} : {:>12.5f} s\n'.format('Test Time',t2))
        if debug==2: quit()
    return numpy.mean(test_loss)

def evaluate(data, model, loss_function, update=False, **kwargs):
    if update and data['y_data'].shape[-1]==1:
        input_data = data['X_data'][0].reshape(1,*data['X_data'].shape[1:])
        y_predicted = []
        for i in range(len(data['X_data'])):
            out = model.predict(input_data)
            y_predicted.append(out)
            input_data = numpy.concatenate((input_data,out),axis=2)[:,:,1:]
        y_predicted = numpy.array(y_predicted).reshape(data['y_data'].shape)
    else:
        if update:
            logging.info('\tPrediction on prediction (update parameter on) is not implemented for NN output size higher than unity.')
        y_predicted = model.predict(data['X_data'])
    acc = get_accuracy(y_predicted,data['y_data'].squeeze())
    acc /= len(data['y_data'])
    loss = loss_function(data['y_data'].squeeze(),y_predicted.squeeze()).numpy()
    return numpy.mean(loss), 100*acc

def get_accuracy(output,label):
    preds = numpy.argmax(output,axis=1)
    n_correct = numpy.equal(preds,label).sum()
    return n_correct