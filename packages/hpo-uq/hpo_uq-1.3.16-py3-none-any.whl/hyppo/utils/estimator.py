# External
import numpy

# Local
from .sampling import sampling
from ..train import train_evaluation

def estimate(config,**kwargs):
    """
    Processing time calculator. This function evaluation
    """
    samples = sampling(**config['prms'])
    nodes = config['dist']['sbatch']['nodes']
    cores = 32*nodes
    assert len(samples)==config['prms']['nevals'], 'Number of recorded samples must the same than number of evaluations in configuration file. Abort.'
    if 'epochs' not in config['prms']['names']:
        assert 'epochs' in config['prms']['default'], 'Can find default value for number of epochs'
        epochs = config['prms']['default']['epochs']
    idxs = [samples[:,1].argmin(),samples[:,1].argmax()]
    times = numpy.empty((0,2))
    epoch_time, test_time = 0, 0
    for samples in samples[idxs]:
        mult = config['prms']['mult']
        x_sc = [int(samples[n])*mult[n] for n in range(len(mult))]
        x_sc = {name:value for name,value in zip(config['prms']['names'],x_sc)}
        times = numpy.vstack((times,train_evaluation(x_sc,config,debug=True)))
    epoch_time = numpy.average(times[:,0])
    test_time = numpy.average(times[:,1])
    times = [0]*cores
    for i in range(cores):
        for ii in numpy.arange(config['hpo']['nevals'])[i::mpi_cores]:
            times[i] += ( ( epoch_time*samples[ii,0] + test_time ) * config['model']['trial'] )
    print('Maximum estimated time for %i evaluations done over %i trials across %i cores:\n\n\t%.2f hours\n'%(config['hpo']['nevals'],config['model']['trial'],mpi_cores,max(times)/60./60.))

