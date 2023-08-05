# Internals
import math

# Externals
import numpy

# Locals
from .phi import phi

def InitialRBFMatrices(PairwiseDistance,samples,phifunction='cubic',
                       polynomial='linear',**kwargs):
    PHI = numpy.zeros((samples.shape[0], samples.shape[0]))
    if phifunction == 'linear':
        PairwiseDistance = PairwiseDistance
    elif phifunction == 'cubic':
        PairwiseDistance = PairwiseDistance ** 3
    elif phifunction == 'thinplate':
        PairwiseDistance = PairwiseDistance ** 2 * math.log(PairwiseDistance + numpy.finfo(numpy.double).tiny)
    PHI = PairwiseDistance
    phi0 = phi(0, phifunction) # phi-value where distance of 2 points =0 (diagonal entries)
    if polynomial == 'None':
        pdim = 0
        P = numpy.array([])
    elif polynomial == 'constant':
        pdim = 1
        P = numpy.ones((samples.shape[0], 1)), samples
    elif polynomial == 'linear':
        pdim = samples.shape[1] + 1
        P = numpy.concatenate((numpy.ones((samples.shape[0], 1)), samples), axis = 1)
    elif polynomial == 'quadratic':
        pdim = (samples.shape[1] + 1) * (samples.shape[1] + 2) // 2
        P = numpy.concatenate((numpy.concatenate((numpy.ones((samples.shape[0], 1)), samples), axis = 1),
                               numpy.zeros((samples.shape[0], (samples.shape[1]*(samples.shape[1]+1))//2))), axis = 1)
    else:
        raise myException('Error: Invalid polynomial tail.')
    return numpy.asmatrix(PHI), numpy.asmatrix(P), pdim

def UpdateRBFMatrices(samples, PHI, P, PairwiseDistance, r, phifunction='cubic', polynomial='linear', **kwargs):
    phi0 = phi(0, phifunction)
    new_phi = phi(r, phifunction).squeeze()
    PHI_new = numpy.zeros((len(samples), len(samples)))
    PHI_new[:PHI.shape[0],:PHI.shape[1]] = numpy.array(PHI)
    PHI_new[-1,0:new_phi.shape[1]] = new_phi
    PHI_new[0:new_phi.shape[1],-1] = new_phi
    PHI_new[-1,-1] = phi0
    if polynomial == 'None':
        P = numpy.array([])
    elif polynomial == 'constant':
        P = numpy.ones((len(samples), 1)), samples
    elif polynomial == 'linear':
        P = numpy.concatenate((numpy.ones((len(samples), 1)), samples), axis = 1)
    elif polynomial == 'quadratic':
        P = numpy.concatenate((numpy.concatenate((numpy.ones((samples.shape[0], 1)), samples), axis = 1),
                               numpy.zeros((samples.shape[0], (samples.shape[1]*(samples.shape[1]+1))//2))), axis = 1)
    return numpy.asmatrix(PHI_new), numpy.asmatrix(P)
