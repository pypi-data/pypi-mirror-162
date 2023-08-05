# System
import os
import time
import array
import random
import logging

# External
import numpy
import scipy.spatial as scp
import pickle5 as pickle
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from deap import base
from deap import creator
from deap import tools

# Local
from ..train import train_evaluation
from ..obj_fct import *
from ..utils import extract_evals, check_surrogate_sample

def gp(config,log_dir,step,rank,xlow,xup,mult,names,loops=1000,istop=None,
       nhof=10,ngen=100,mu=100,cxpb=0.75,indpb=0.1,default={},**kwargs):
    """
    Gaussian Process based surrogate optimization algorithm.

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
    nbof : :class:`int`
      Number of best individuals to keep in the hall of fame
    ngen : :class:`int`
      Number of generations to run during genetic process
    mu : :class:`int`
      Number of individuals in the genetic population
    cxpb : :class:`float`
      Cross-over probability
    indpb : :class:`float`
      Independent probability for each individual to be exchanged
    default : :class:`dict`
      Dictionary of default hyperparameter values
    """
    out_path = 'original'
    # Build Gaussian Process based on input-output pairs
    gpr = GaussianProcessRegressor(kernel=RBF(),
                                   #alpha=1e-6,
                                   normalize_y=True,
                                   #n_restarts_optimizer=5,
                                   #random_state=125,
                                   #random_state=0,
                                   )
    # Print out parameters for generational process
    logging.info('='*40)
    logging.info('GAUSSIAN PROCESS PARAMETERS')
    logging.info('-'*40)
    logging.info('Hall Of Fame size      : {}'.format(nhof))
    logging.info('Number of generations  : {}'.format(ngen))
    logging.info('Number of individuals  : {}'.format(mu))
    logging.info('Cross-over probability : {}'.format(cxpb))
    logging.info('Mutation probability   : {}'.format(indpb))
    logging.info('='*40+'\n')
    # Loop through evaluations
    for iloop in range(loops):
        logging.info('='*40)
        logging.info('SURROGATE ITERATION {:>3} / {:<3}'.format(iloop+1,loops))
        logging.info('-'*40)
        if rank == 0:
            # Gather results, fit and save GP model
            samples, fvals, Fbest, gpr = get_and_fit(log_dir,gpr,out_path)
            # Initialize genetic algorithm
            if iloop==0:
                toolbox, stats = setup(gpr, samples, fvals, xlow, xup, indpb)
            else:
                toolbox.unregister("evaluate")
                toolbox.register("evaluate", Expected_improvement, samples=samples, fvals=fvals, gpr=gpr)
            pf = tools.ParetoFront()
            logbook = tools.Logbook()
            logbook.header = "gen", "evals", "std", "min", "avg", "max"
            pop = toolbox.population(n=mu)
            hof = tools.HallOfFame(nhof)
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            fits = [ind.fitness.values[0] for ind in pop]
            pop = toolbox.select(pop, len(pop))
            hof.update(pop)
            record = stats.compile(pop)
            logbook.record(gen=0, evals=len(invalid_ind), **record)
            t0 = time.time()
            # Begin the evoluation
            for gen in range(1, ngen+1):
                # Vary the population
                offspring = tools.selNSGA2(pop, len(pop))
                offspring = tools.selTournamentDCD(pop, len(pop))
                offspring = [toolbox.clone(ind) for ind in offspring]
                for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
                    if len(ind1)>1 and random.random() <= cxpb:
                        toolbox.mate(ind1, ind2)
                    toolbox.mutate(ind1)
                    toolbox.mutate(ind2)
                    del ind1.fitness.values, ind2.fitness.values
                # Evaluate the individuals with an invalid fitness
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit
                pop[:] = offspring
                hof.update(offspring)
                record = stats.compile(pop)
                logbook.record(gen=gen, evals=len(invalid_ind), **record)
            logging.info('Total of sample sets used : %i' % len(samples))
            logging.info('Generational process time : %.3f s' % (time.time()-t0))
            logging.info('Best loss value so far    : %.5f' % Fbest)
            logging.info('-'*40)
            while os.path.exists('wait'):
                continue
            os.system('touch wait')
            samples = extract_evals(log_dir)[-1]
            # Find next set of hyperparameters
            xselected = []
            for ii in range(nhof):
                ed = scp.distance.cdist(numpy.asmatrix(hof[ii]), samples, 'euclidean')
                if numpy.min(ed)>=1:
                    xselected = numpy.asarray(hof[ii])
                    break
            while len(xselected)==0: #no new point was selected, use a random one
                x_=numpy.zeros(samples.shape[1])
                for ii in range(samples.shape[1]):
                    x_[ii] = random.randint(xlow[ii], xup[ii])
                if numpy.min(scp.distance.cdist(numpy.asmatrix(x_), samples, 'euclidean'))>=1:
                    xselected=x_
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
        res = train_evaluation(x_sc,xselected,output=out_path,**config)
        logging.info('='*40+'\n')
        # Stopping criteria
        if istop!=None and len(get_and_fit(log_dir,gpr,out_path,fit=False)[0])>=istop:
            break
    # Gather results, fit and save GP model
    samples, fvals, Fbest, gpr = get_and_fit(log_dir,gpr,out_path)
        
def setup(gpr,samples,fvals,xlow,xup,indpb=0.1):
    #set up the GP to maximize expected improvement over an integer lattice
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,)) 
    # Individuals in the generation
    creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)
    toolbox = base.Toolbox()
    for ii in range(samples.shape[1]):
        INT_MIN, INT_MAX = xlow[ii], xup[ii]
        toolbox.register("attr_int_"+str(ii), random.randint, INT_MIN, INT_MAX)
    toolbox_list=[]
    for i in range(samples.shape[1]):
        toolbox_list.append(eval("toolbox.attr_int_"+str(i)))
    toolbox.register("individual", tools.initCycle, creator.Individual,tuple(toolbox_list),n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", Expected_improvement, samples=samples, fvals=fvals, gpr=gpr)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=list(xlow), up=list(xup), indpb=indpb)
    toolbox.register("select", tools.selNSGA2)
    # Initialize statistical functions
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)
    return toolbox, stats

def Expected_improvement(x, samples, fvals, gpr):
    """
    Calculate expected improvement.

    Parameters
    ----------
    
    x : :class:`deap.creator.Individual`
      Trial set of hyperparameters

    opti : :class:`hyppo.surrogate.utility.Optimization`
      Object containing all information

    References
    ----------

    `This blog about Bayesian Optimization <https://krasserm.github.io/2018/03/21/bayesian-optimization/#expected-improvement>`_
    """
    x = numpy.array(x).reshape(-1, samples.shape[1])
    mu, sigma = gpr.predict(x, return_std=True)
    sigma = sigma.reshape(-1, 1)
    mu_sample_opt = numpy.min(fvals)
    with numpy.errstate(divide='ignore'):
        imp = - (mu - mu_sample_opt)
        Z = imp / sigma
        expected_improvement = imp * norm.cdf(Z) + sigma * norm.pdf(Z)
        expected_improvement[sigma == 0.0] = 0.0
    answer=-1.*expected_improvement[0,0] #maximize f = minimize -f
    return answer,

def get_and_fit(log_dir,gpr,out_path,fit=True):
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
    if fit:
        # Gaussian Process fitting
        gpr.fit(samples, fvals)
        # Save surrogate models
        path = os.path.join(log_dir,'models',out_path)
        os.makedirs(path,exist_ok=True)
        with open(path+'/gpr_model.pkl','wb') as f:
            pickle.dump(gpr,f)
    return samples, fvals, Fbest, gpr

