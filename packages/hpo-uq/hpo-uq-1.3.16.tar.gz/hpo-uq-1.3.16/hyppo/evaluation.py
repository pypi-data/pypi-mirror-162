# System
import os
import glob
import logging

# External
import numpy
import pickle5 as pickle

# Local
from .train import train_evaluation
from .utils import make_samples, make_tables

def evaluation(config):
    """
    Execute initial evaluations in parallel. This function uses the
    `mpi4py <https://mpi4py.readthedocs.io/en/stable/>`__ package and
    loop through all random hyperparameter sets to execute them across
    all available processors. This function does not handle distributed
    training for individual evaluations. In order to execute individual
    trainings in parallel, the :ref:`nested parallelization<nested>`
    approach can be used.
    
    Parameters
    ----------
    config : :class:`dict`
      Input configuration dictionary
    samples : :class:`dict`
      Random hyperparameter values
    """
    logging.info('='*40)
    logging.info('CONFIGURATION:')
    logging.info('-'*40 + '\n\n%s\n' % config['original'])
    # Extract task information
    step   = config['dist']['step']
    nsteps = config['dist']['nsteps']
    rank   = config['dist']['rank']
    split  = config['dist']['split']
    trial  = config['model']['trial']
    # Make / extract samples
    samples = make_samples(**config['prms'])
    logging.info('='*40+'\n')
    # Select samples to be executed sequentially in the step
    for ii in numpy.arange(len(samples))[step::nsteps]:
        if split=='data' or (split=='trial' and rank<trial):
            logging.info('='*40)
            single_evaluation(ii,samples,**config)
            logging.info('='*40+'\n')
    
def single_evaluation(ii,samples,prms,**kwargs):
    logging.info('EVALUATION {:>3} / {:<3}'.format(ii+1,len(samples)))
    logging.info('Samples: %s' % samples[ii])
    # Create hyperparameter set
    x_sc = [int(samples[ii, n])*prms['mult'][n] for n in range(len(prms['mult']))]
    x_sc = {name:value for name,value in zip(prms['names'],x_sc)}
    if 'default' in prms.keys() and type(prms['default'])==dict:
        x_sc = {**x_sc,**prms['default']}
    output = '_'.join(numpy.array(samples[ii],dtype=str))
    res = train_evaluation(x_sc,samples[ii],output='evaluation_%s'%output,**kwargs)
