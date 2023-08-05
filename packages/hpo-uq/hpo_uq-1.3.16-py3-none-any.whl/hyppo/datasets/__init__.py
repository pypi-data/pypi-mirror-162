# System
import importlib

def get_data(dataset,**kwargs):
    """
    Top-level factory function for getting your models.
    """
    module = importlib.import_module('.' + dataset, 'hyppo.datasets')
    return module.get_data(**kwargs)

def get_loader(data,batch,library,**kwargs):
    """
    Top-level factory function for getting your models.
    
    Parameters
    ----------
    batch :
      Extracted from hyperprms dictionary
    library :
      Extracted from model dictionary
    """
    if library=='pt':
        module = importlib.import_module('.loaders', 'hyppo.datasets')
        return module.get_loader(data,batch,**kwargs)
    else:
        return data
