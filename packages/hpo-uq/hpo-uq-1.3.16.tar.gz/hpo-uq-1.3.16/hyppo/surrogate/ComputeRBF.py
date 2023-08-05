#----------------********************************--------------------------
# Copyright (C) 2013 Cornell University
# This file is part of the program StochasticRBF.py
#
#    StochasticRBF.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StochasticRBF.py is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StochasticRBF.py.  If not, see <http://www.gnu.org/licenses/>.
#----------------********************************--------------------------

#----------------*****  Contact Information *****--------------------------
#   Primary Contact (Implementation Questions, Bug Reports, etc.):
#   Juliane Mueller: juliane.mueller2901@gmail.com
#       
#   Secondary Contact:
#       Christine A. Shoemaker: cas12@cornell.edu
#       Haoyu Jia: leonjiahaoyu@gmail.com
#----------------********************************--------------------------
import numpy
import scipy.spatial as scp
from .phi import phi

class ComputeRBF():
    '''ComputeRBF predicts the objective function values of the candidate points
    and also returns the distance of each candidate point to all already
    sampled points

    Input: 
    CandPoint: (Ncand x dimension) matrix with candidate points for next
    expensive function evaluation
    Data: struct-variable with all problem information

    Output:
    RBFVALUE: objective function value predicted by RBF model
    NORMVALUE: matrix with distances of all candidate points to already
    sampled points
    '''
    def __init__(self,phifunction='cubic',polynomial='linear',**kwargs):
        self.phifunction = phifunction
        self.polynomial  = polynomial
        
    def update(self,samples,llambda,ctail):
        self.samples = samples
        self.llambda = llambda
        self.ctail   = ctail

    def fit(self,CandPoint):
        numpoints = CandPoint.shape[0] # determine number of candidate points
        # compute pairwise distances between candidates and already sampled points
        Normvalue = numpy.transpose(scp.distance.cdist(CandPoint, self.samples))
        # compute radial basis function value for distances
        U_Y = phi(Normvalue, self.phifunction)
        num_response_surfs = len(self.llambda)
        RBFvalue = numpy.asmatrix(numpy.zeros((numpoints,num_response_surfs)))
        for k in range(num_response_surfs):
            # determine the polynomial tail (depending on rbf model)
            if self.polynomial == 'none':
                PolyPart = numpy.zeros((numpoints, 1))
            elif self.polynomial == 'constant':
                PolyPart = self.ctail[k] * numpy.ones((numpoints, 1))
            elif self.polynomial == 'linear':
                PolyPart = numpy.asmatrix(numpy.concatenate((numpy.ones((numpoints, 1)), CandPoint), axis = 1)) * numpy.asmatrix(self.ctail[k])
            elif self.polynomial == 'quadratic':
                PolyPart = numpy.concatenate((numpy.concatenate((numpy.ones((numpoints, 1)), CandPoint), axis = 1), \
                                              numpy.zeros((numpoints, (self.samples.shape[1] * (self.samples.shape[1] + 1)) // 2))), axis = 1) * numpy.asmatrix(self.ctail[k])
            else:
                raise myException('Error: Invalid polynomial tail.')
            RBFvalue[:,k] = numpy.asmatrix(U_Y).T * numpy.asmatrix(self.llambda[k]) + PolyPart
        if num_response_surfs == 1:
            return RBFvalue, numpy.asmatrix(Normvalue)
        else:
            c1 = numpy.mean(RBFvalue,axis=1)
            c2 = numpy.std(RBFvalue,axis=1)
            RBFvalue = numpy.concatenate((c1,c2),axis=1)
            return RBFvalue, numpy.asmatrix(Normvalue)

    def predict(self,X,return_std=False):
        return numpy.array(self.fit(X)[0])
        
