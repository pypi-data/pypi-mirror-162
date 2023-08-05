import importlib

def training(library, **kwargs):
    """
    Top-level factory function for getting your models.

    Parameters
    ----------
    library : :py:class:`str`
      Machine Learning library to be used.
    
    Returns
    -------
    train_out : :py:class:`dict`
      Output of training function.
    """
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.' + library, 'hyppo.dnnmodels')
    return module.train(**kwargs)

def inference(library, **kwargs):
    """
    Top-level factory function for getting your models.

    Parameters
    ----------
    library : :py:class:`str`
      Machine Learning library to be used.
    
    Returns
    -------
    train_out : :py:class:`dict`
      Output of training function.
    """
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.' + library, 'hyppo.dnnmodels')
    return module.inference(**kwargs)

def get_fct(library, **kwargs):
    """
    Top-level factory function for getting your models.
    """
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.' + library + '.utils', 'hyppo.dnnmodels')
    return module.get_fct(**kwargs)

def mcd(library, **kwargs):
    """
    Top-level factory function for getting your models.
    """
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.' + library, 'hyppo.dnnmodels')
    return module.mcd(**kwargs)

def uq_quantifier(trainer, library=None, **kwargs):
    """
    Top-level factory function for getting your models.
    """
    library = {'pt':'pytorch','tf':'tensorflow'}[library]
    module = importlib.import_module('.' + library + '.uq', 'hyppo.dnnmodels')
    return module.uq_quantifier(trainer,**kwargs)
