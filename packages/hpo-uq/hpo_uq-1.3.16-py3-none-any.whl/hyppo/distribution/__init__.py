# System
import importlib

def get_workers(dist,model,**kwargs):
    """
    Top-level factory function for intializing the workers.
    """
    if 'library' in model.keys():
        return backend_from_library(dist,**model,**kwargs)
    else:
        return {'rank':0, 'size':1, 'device':None, 'device_ids':None}

def backend_from_library(dist,trainer,library=None,**kwargs):
    assert library in ['pt','tf'], 'ML library not recognized. Abort'
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.'+library, 'hyppo.distribution')
    return module.init_workers(trainer,**dist)
    