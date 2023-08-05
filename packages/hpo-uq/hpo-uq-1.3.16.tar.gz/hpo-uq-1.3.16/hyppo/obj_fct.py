# Externals
import numpy
from sklearn.metrics import mean_squared_error

def calculate_outer_loss(losses,obj=None,**kwargs):
    if obj==None:
        return numpy.nanmean(losses)
    else:
        return eval(obj)

def sigmoid(losses,**kwargs):
    outer_losses = 1/(1 + numpy.exp(-losses))
    return outer_losses

