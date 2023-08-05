import numpy

def test_problem_1d(X,**kwargs):
    return -(-numpy.sin(3*X) - X**2 + 0.7*X)

def test_problem_2d(X,Y,**kwargs):
    R = numpy.sqrt(X**2 + Y**2)
    Z = 0.4 - (1. / numpy.sqrt(2 * numpy.pi)) * numpy.exp(-.5*R**2)
    return Z
