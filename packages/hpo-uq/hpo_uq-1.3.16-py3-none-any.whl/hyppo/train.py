# System
import os
import sys
import logging
import importlib
import time
import types

# External
import yaml
import numpy
import pickle5 as pickle

# Local
from .datasets import get_loader
from .dnnmodels import training, mcd, uq_quantifier
from .hyperparams import get_hyperprms
from .utils.extract import gather_trials, check_evaluation_outer_loss
from .obj_fct import calculate_outer_loss
from .utils.problems import *

def train_evaluation(x_sc, samples, trainer, model, dist, output='out', data={}, uq={}, **kwargs):
    """
    Execute training according to requested trainer mode. This function looks at the
    trainer mode requested in the configuration file and initiate the training
    accordingly.
    
    Parameters
    ----------
    x_sc : :class:`dict`
      Random hyperparameter set. Each key corresponds to the hyperparameter names
      and the corresponding value to the randomly selected sample value.
    samples : :class:`numpy.ndarray`
      Random hyperparameter integer values for single target evaluation.
    trainer : :class:`str`
      Trainer mode to be used.
    model : :class:`dict`
      Model setting extracted from the YAML configuration file.
    output : :class:`str`
      Directory name to save output training results.
    data : :class:`dict`
      Data setting extracted from the YAML configuration file (empty by default).
    uq : :class:`dict`
      Uncertainty quantification parameter setting extracted from the YAML configuration
      file (empty by default).

    Returns
    -------
    res : :class:`float`
      Output of objective function.
    """
    # Start timer for recording function evaluation time
    start_time = time.time()
    # Display hyperparameter set only once, before the first trial
    hyperprms = get_hyperprms(trainer, x_sc, **model)
    # Prepare list of trial indexes to be evaluated in rank
    trials = numpy.arange(model['trial'])
    if dist['split']=='trial':
        trials = trials[dist['rank']::dist['size']]
    loaders = get_loader(data, **hyperprms, **model, **dist) if trainer=='internal' else None
    # Loop through all selected trials
    for i in trials:
        out_path = '%s/%02i/' % (output,i+1)
        if trainer=='internal':
            run_args = {'itrial':i,'data':loaders,'hyperprms':hyperprms,'output':out_path}
            loss = training(**run_args,**model,**dist)
        else:
            run_args = {'itrial':i,'x_sc':x_sc,'trainer':trainer,'output':out_path}
            loss = external_training(**run_args,**model,**dist)
    # Check if all losses over all trials are found
    res = None
    if dist['rank']==0:
        while len(gather_trials(samples,output,**model,**dist)) != model['trial']:
            continue
        losses = gather_trials(samples,output,**model,**dist)
        if 'mcd' in uq.keys() and uq['mcd']==True:
            run_args['output'] = output
            valid_trials = numpy.argwhere(~numpy.isnan(losses) & ~numpy.isinf(losses)).squeeze()
            logging.info('-'*40)
            logging.info('UNCERTAINTY QUANTIFICATION {:>6} MODELS'.format(len(valid_trials)))
            logging.info('-'*40)
            if trainer=='internal':
                inner_loss, unc = mcd(trials=valid_trials,**run_args,**model,**dist,**uq)
            else:
                inner_loss, unc = external_mcd(trials=valid_trials,**run_args,**model,**dist,**uq)
            if numpy.isnan(unc) or numpy.isinf(unc) or numpy.isnan(inner_loss):
                outer_loss = float('nan')
                inner_loss = float('nan')
                unc        = float('nan')
            else:
                outer_loss = calculate_outer_loss(inner_loss,**model)
        else:
            if numpy.isnan(losses).all():
                outer_loss = float('nan')
                inner_loss = float('nan')
                unc        = float('nan')
            else:
                outer_loss = calculate_outer_loss(losses,**model)
                inner_loss = numpy.nanmean(losses)
                unc        = numpy.nanstd(losses)
        res = outer_loss
        logging.info('-'*40)
        logging.info('OUTER OBJECTIVE FUNCTION {:>8} TRIALS'.format(len(losses)))
        logging.info('-'*40)
        logging.info('{:>14} : {:>11.5f}'.format('Outer Loss',outer_loss))
        logging.info('{:>14} : {:>11.5f}'.format('Inner Loss',inner_loss))
        logging.info('{:>14} : {:>11.5f}'.format('Uncertainty',unc))
    else:
        logging.info('-'*40)
        logging.info('Waiting for other processes to finish...')
        while check_evaluation_outer_loss(samples,output,**dist)==False:
            continue
    logging.info('-'*40)
    logging.info("Execution Time : %.3f s" % (time.time() - start_time))
    return res

def external_training(itrial=0, trial=1, x_sc=None, trainer=None, output=None, log_dir=None, output_dir=None, yaml_input=None, **kwargs):
    start_time = time.time()
    logging.info('-'*40)
    logging.info('{} {:>3} / {:<3} {:>24}'.format('TRIAL',itrial+1,trial,'TRAINING'))
    logging.info('-'*40)
    if output_dir==None or os.path.exists(output_dir):
        out = {'output_dir':os.path.join(log_dir,'output',output)}
    else:
        out = {output_dir:os.path.join(log_dir,'output',output)}
    if yaml_input!=None:
        params = yaml_creation(x_sc,output_dir,**yaml_input)
    else:
        params = {**out,**x_sc,**kwargs}
    if '.' not in trainer and 'test_problem' in trainer:
        loss = eval(trainer)(**params)
    elif type(trainer)==types.FunctionType:
        loss = trainer(**params)
    else:
        modlist = trainer.split('.')
        module = importlib.import_module('.' + modlist[-2], '.'.join(modlist[:-2]))
        loss = eval('module.'+modlist[-1])(**params)
    logging.info('-'*40)
    logging.info('{} {:>3} / {:<3} {:>24}'.format('TRIAL',itrial+1,trial,'TESTING'))
    logging.info('-'*40)
    logging.info('\t Test Loss : {:>11.5f}'.format(loss))
    logging.info('\tTrain Time : {:>11.5f} s'.format(time.time()-start_time))
    return loss

def external_mcd(x_sc=None, trainer=None, output=None, log_dir=None, output_dir=None, **kwargs):
    if output_dir==None or os.path.exists(output_dir):
        out = {'output_dir':os.path.join(log_dir,'output',output)}
    else:
        out = {output_dir:os.path.join(log_dir,'output',output)}
    params = {**out,**x_sc,**kwargs}
    params['trainer_out'] = True
    modlist = trainer.split('.')
    module = importlib.import_module('.' + modlist[-2], '.'.join(modlist[:-2]))
    trainer = eval('module.'+modlist[-1])(**params)
    inner_loss, unc = uq_quantifier(trainer, **kwargs)
    return inner_loss, unc

def yaml_creation(x_sc,output_dir,src,config=None,**kwargs):
    # Extract input configuration file
    with open(src) as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    # Update parameters
    if config==None:
        params = {**params,**x_sc}
    else:
        params[config] = {**params[config],**x_sc}
    # Save new input configuration file
    os.makedirs(output_dir,exist_ok=True)
    yaml_config = os.path.join(output_dir,'config.yaml')
    with open(yaml_config, 'w') as f:
        yaml.dump(params, f, default_flow_style=False)
    params = {'yaml_config':yaml_config,'config':config,**kwargs}
    return params
