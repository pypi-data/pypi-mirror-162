# System
import os
import copy
import math
import time
import logging

# External
import numpy
import numpy.matlib as npm
import scipy.spatial as scp
import pickle5 as pickle
#from pyDOE import *

# Local
from ..train import train_evaluation
from ..utils import extract_evals, check_surrogate_sample
from .phi import phi
from .InitialRBFMatrices import InitialRBFMatrices, UpdateRBFMatrices
from .ComputeRBF import ComputeRBF

def rbf(config,log_dir,step,rank,xlow,xup,mult,names,loops=1000,maxshrinkparam=5,istop=None,
        succtolerance=3,Ncand=500,valweight=1.25,maxvalweight=1,default={},**kwargs):
    """
    Radial Basis Function based surrogate optimization algorithm.    

    Parameters
    ----------
    config : :class:`dict`
      Configuration dictionary object to be used when evaluating subsequent sample sets.
    log_dir : :class:`str`
      Relative path where log files are stored
    loops : :class:`int`
      Number of iterations to do surrogate modeling over.
    step : :class:`int`
      Current SLURM step
    rank : :py:class:`int`
      Current processor rank
    xlow : :class:`list` [ :class:`int` ]
      Lower boundaries of hyperparameters to evaluate.
    xup : :class:`list` [ :class:`int` ]
      Upper boundaries of hyperparameters to evaluate.
    mult : :class:`list` [ :class:`int` ]
      Scaling factor for each hyperparameter
    names : :class:`list` [ :class:`str` ]
      Name of each hyperparameter
    maxshrinkparam : :class:`int`
      Maximal number of shrinkage of standard deviation for normal distribution when generating the candidate points
    succtolerance : :class:`int`
      Success tolerance
    default : :class:`dict`
      Dictionary of default hyperparameter values
    """
    out_path = 'original'
    # Initialize RBF class
    rbf = ComputeRBF(**kwargs)
    # Print out parameters for generational process
    logging.info('='*40)
    logging.info('RADIAL BASIS FUNCTION PARAMETERS')
    logging.info('-'*40)
    logging.info('Maximum shrinkage : {}'.format(maxshrinkparam))
    logging.info('Success tolerance : {}'.format(succtolerance))
    logging.info('='*40+'\n')
    # Loop through evaluations
    for iloop in range(loops):
        logging.info('='*40)
        logging.info('SURROGATE ITERATION {:>3} / {:<3}'.format(iloop+1,loops))
        logging.info('-'*40)
        if rank == 0:
            # Gather results, fit and save GP model
            samples, fvals, xbest, Fbest = get_fvals(log_dir)
            valweight -= 0.25
            if valweight<0:
                valweight = maxvalweight
            if iloop==0:
                # Build the surrogate - Determine pairwise distance between points
                PairwiseDistance = scp.distance.cdist(samples, samples, 'euclidean')
                # Build the surrogate - Initial RBF matrices
                PHI, P, pdim = InitialRBFMatrices(PairwiseDistance,samples,**kwargs)
            else:
                # update PHI matrix only if planning to do another iteration
                PHI, P = UpdateRBFMatrices(samples, PHI, P, PairwiseDistance, r=normval[0], **kwargs)
            # Initialize array with function values
            #fvals = numpy.asmatrix(numpy.zeros(fvals.shape))
            # number of new samples in an iteration
            #NumberNewSamples = min(data.nns,data.maxeval - data.m)
            # replace large function values by the median of all available function values
            #Ftransform = numpy.copy(numpy.asarray(data.Y)[0:data.m])
            #medianF = numpy.median(numpy.asarray(data.Y)[0:data.m])
            #Ftransform[Ftransform > medianF] = medianF
            # Fit the response surface - Compute RBF parameters
            a_part1 = numpy.concatenate((PHI, P), axis = 1)
            a_part2 = numpy.concatenate((numpy.transpose(P), numpy.zeros((pdim, pdim))), axis = 1)
            a = numpy.concatenate((a_part1, a_part2), axis = 0)
            eta = math.sqrt((1e-16) * numpy.linalg.norm(a, 1) * numpy.linalg.norm(a, numpy.inf))
            if fvals.shape[1]==1:
                coeff = numpy.linalg.solve((a + eta * numpy.eye(len(samples) + pdim)),
                                        numpy.concatenate((fvals[:,:1], numpy.zeros((pdim, 1))), axis = 0))
                # llambda is not a typo, lambda is a python keyword
                llambda = [coeff[0:len(samples)]]
                ctail = [coeff[len(samples): len(samples) + pdim]]
            else:
                a_inv   = numpy.linalg.inv(a + eta * numpy.eye(len(samples) + pdim))
                llambda = []
                ctail   = []
                for i in range(30): #This generates 30 different response surfaces using the CIs
                    indx  = numpy.random.choice(range(3),(len(samples),1))
                    rhs   = numpy.asmatrix([fvals[k,indx[k,0]] for k in range(len(samples))]).T
                    rhs   = numpy.concatenate((rhs,numpy.zeros((pdim,1))),axis=0)
                    coeff = numpy.matmul(a_inv,rhs)
                    llambda.append(coeff[0:len(samples)])
                    ctail.append(coeff[len(samples): len(samples)+pdim])
                llambda = llambda
                ctail   = ctail
            rbf.update(samples,llambda,ctail)
            save_model(log_dir,out_path,rbf)
            logging.info('Total of sample sets used : %i' % len(samples))
            logging.info('Best loss value so far    : %.5f' % Fbest)
            logging.info('-'*40)
            while os.path.exists('wait'):
                continue
            os.system('touch wait')
            samples = extract_evals(log_dir)[-1]
            # Find next set of hyperparameters
            # Introduce candidate points  -- update later when number of nodes >1
            # CandPoint = numpy.asmatrix(data.val_list).T #this needs to be updated when we're 
            # create candidate point:
            # perturb xbest - local perturbations: 1 or 2 for parameters 1 and 2, 1 for parameters 3 and 4
            C1 = npm.repmat(xbest, Ncand, 1)
            R  = numpy.zeros((Ncand, samples.shape[1]))
            for ii in range(samples.shape[1]):
                R[:,ii]=numpy.ravel(numpy.random.randint(0,3,(Ncand,1))*numpy.random.choice(numpy.array([-1,1]),(Ncand,1)))
            CP = R + C1
            # Reflect outsiders over boundary to inside
            for ii in range(samples.shape[1]):
                vec_ii = CP[:, ii]
                adj_l = numpy.where(vec_ii < xlow[ii])
                vec_ii[adj_l[0]] = xlow[ii] + (xlow[ii] - vec_ii[adj_l[0]])
                adj_u = numpy.where(vec_ii > xup[ii])
                vec_ii[adj_u[0]] = xup[ii] - (vec_ii[adj_u[0]]-xup[ii])
                stillout_u = numpy.where(vec_ii > xup[ii])
                vec_ii[stillout_u[0]] = xlow[ii]
                stillout_l = numpy.where(vec_ii < xlow[ii])
                vec_ii[stillout_l[0]] = xup[ii]
                CP[:, ii] = copy.copy(vec_ii)
            # Generate second set of randomly generated points
            CR = numpy.zeros((Ncand, samples.shape[1]))
            for ii in range(samples.shape[1]):
                CR[:,ii]=numpy.ravel(numpy.random.randint(xlow[ii],xup[ii],(Ncand,1)))
            CandPoint = numpy.concatenate((CP,CR), axis = 0)#all candidate points
            CandValue, NormValue = rbf.fit(CandPoint)
            xselected, normval = Minimize_Merit_Function(CandPoint, CandValue, NormValue, fvals, valweight)
            xselected = numpy.array(xselected,dtype=int)
            logging.info('Samples: %s' % xselected)
            os.system('rm wait')
        else:
            logging.info('Surrogate modeling in progress...')
            while check_surrogate_sample(log_dir,step,iloop)==[]:
                continue
            xselected = check_surrogate_sample(log_dir,step,iloop)
            logging.info('Samples: %s' % xselected)
        # Execute training
        x_sc = {name:int(sample)*scale for name,sample,scale in zip(names,xselected,mult)}
        x_sc = {**x_sc,**default}
        out_path = 'surrogate_%s' % ('_'.join(numpy.array(xselected,dtype=str)))
        Fselected = train_evaluation(x_sc,xselected,output=out_path,**config)
        logging.info('='*40+'\n')
        # Stopping criteria
        if istop!=None and len(get_fvals(log_dir)[0])>=istop:
            break

def Minimize_Merit_Function(CandPoint, CandValue, NormValue, fvals, valueweight):
    if fvals.shape[1]>1:
        #CandValue = CandValue[:,0] #mean value computed for each candiate point of the rbf ensembles
        CandValue = CandValue[:,0]+2*CandValue[:,1] #mean + 2std  
    MinCandValue = numpy.amin(CandValue)
    MaxCandValue = numpy.amax(CandValue)
    if MinCandValue == MaxCandValue:
        ScaledCandValue = numpy.ones((CandValue.shape[0], 1))
    else:
        ScaledCandValue = (CandValue - MinCandValue) / (MaxCandValue - MinCandValue)
    CandMinDist = numpy.asmatrix(numpy.amin(NormValue, axis = 0)).T
    MaxCandMinDist = numpy.amax(CandMinDist)
    MinCandMinDist = numpy.amin(CandMinDist)
    if MaxCandMinDist == MinCandMinDist:
        ScaledCandMinDist = numpy.ones((CandMinDist.shape[0], 1))
    else:
        ScaledCandMinDist = (MaxCandMinDist - CandMinDist) / (MaxCandMinDist - MinCandMinDist)
    # compute weighted score for all candidates
    CandTotalValue = valueweight * ScaledCandValue + (1 - valueweight) * ScaledCandMinDist
    # assign bad scores to candidate points that are too close to already sampled points
    CandTotalValue[CandMinDist < 1] = numpy.inf
    MinCandTotalValue = numpy.amin(CandTotalValue)
    selindex = numpy.argmin(CandTotalValue)
    xselected = numpy.array(CandPoint[selindex, :])
    #print(xselected)
    normval = {}
    normval[0] = numpy.asmatrix((NormValue[:, selindex])).T
    return xselected, normval

def get_fvals(log_dir):
    """
    Extract results, fit and save GP model.
    """
    # Extract values
    samples, fvals, Fbest, xbest, sets = extract_evals(log_dir)
    # Remove infinite losses
    idxs = numpy.argwhere(numpy.isinf(fvals[:,0]))
    if len(idxs)>0:
        samples = numpy.delete(samples,idxs[:,0],axis=0)
        fvals   = numpy.delete(fvals,idxs[:,0],axis=0)
    return samples, fvals, xbest, Fbest

def save_model(log_dir,out_path,rbf):
    """
    Save surrogate Radial Basis Function model
    """
    path = os.path.join(log_dir,'models',out_path)
    os.makedirs(path,exist_ok=True)
    with open(path+'/rbf_model.pkl','wb') as f:
        pickle.dump(rbf,f)
