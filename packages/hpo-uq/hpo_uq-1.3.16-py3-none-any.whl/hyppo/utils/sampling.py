# System
import os
import random
import logging

# External
import numpy
import yaml
from SALib.sample import saltelli

def sampling(config):
    return make_samples(**config['prms'])

def make_samples(nevals,names,xlow,xup,record=None,salib=False,calc_second_order=False,**kwargs):
    """
    Create random sampling data. The input arguments can be extracted from
    the input configuration file.
    
    Parameters
    ----------
    nevals : :class:`int`
      Total number of initial evaluations to be executed.
    names : :class:`list`
      List, in order, of hyperparameters to be explored.
    xlow : :class:`list`
      Lower bounds on each hyperparameter value.
    xup : :class:`list`
      Upper bounds on each hyperparameter value.
    record : :class:`str`
      ASCII file to save/load the random samples.
    salib : :class:`bool`
      Use sampler from SALib sensitivity analysis package.
      
    Returns
    -------
    samples : :class:`numpy.array`
      Sets of random hyperparameter values.
    """
    problem = None
    n_comb  = hp_comb(xlow, xup)
    logging.info('-'*40)
    # Load recorded sample set
    samples = numpy.empty((0,0))
    pre_loaded = False
    if record!=None and os.path.exists(os.path.expandvars(record)):
        samples = numpy.loadtxt(record,ndmin=2).astype(int)
        pre_loaded = True
    # Create sampling set using SALib
    if salib==True:
        n_samples = nevals*(2+2*len(names)) if calc_second_order else nevals*(2+len(names))
        logging.info('SALib input size      : %i (%i)' % (nevals,n_samples))
        if samples.shape[0]!=n_samples or samples.shape[1]!=len(names):
            if pre_loaded: os.remove(record)
            problem = {
                'num_vars': len(names),
                'names': names,
                'bounds': numpy.array([xlow,xup]).T
            }
            samples = saltelli.sample(problem,nevals,calc_second_order=calc_second_order)
            samples = numpy.array(samples,dtype=int)
    # Create sampling using random generator
    if salib==False:
        if samples.shape[0]!=nevals or samples.shape[1]!=len(names):
            if pre_loaded: os.remove(record)
            if nevals>n_comb:
                nevals = n_comb
            elif nevals<=len(names):
                nevals = len(names) + 1
            samples = numpy.zeros((nevals,len(names)),dtype=int)
            for jj in range(nevals):
                for ii in range(len(names)):
                    samples[jj,ii] = random.randint(xlow[ii], xup[ii])
            rank_P=0
            while rank_P != len(names) + 1:
                for jj in range(nevals):
                    for ii in range(len(names)):
                        samples[jj,ii] = random.randint(xlow[ii], xup[ii])
                P = numpy.concatenate((numpy.ones((nevals, 1)), samples), axis = 1)
                rank_P = numpy.linalg.matrix_rank(P)
    if record!=None and os.path.exists(os.path.expandvars(record))==False:
        numpy.savetxt(record,samples,fmt='%i')
    # Remove duplicate 
    samples, index = numpy.unique(numpy.array(samples),axis=0,return_index=True)
    samples = samples[index.argsort()]
    logging.info('Samples to evaluate   : %i' % len(samples))
    logging.info('Possible combinations : {:,d}'.format(n_comb))
    return samples

def hp_comb(xlow, xup):
    n_comb = 1
    for xmin,xmax in zip(xlow,xup):
        n_comb *= (xmax-xmin+1)
    return n_comb
