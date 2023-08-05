import numpy

def phi(r, type):
    """
    Determines phi-value of distance r between 2 points (depends on chosen RBF model)

    Parameters
    ----------
    r :
      Distance between 2 points
    type : :class:`str`
      RBF model type

    Returns
    -------
    output : 
      Phi-value according to RBF model
 """
    if type == 'linear':
        output = r
    elif type == 'cubic':
        output = numpy.power(r, 3)
    elif type == 'thinplate':
        if r >= 0:
            output = numpy.multiply(numpy.power(r, 2), math.log(r + numpy.finfo(numpy.double).tiny))
        else:
            output = numpy.zeros(r.shape)
    #else:
    #    raise myException('Error: Unkonwn type.')

    return output
