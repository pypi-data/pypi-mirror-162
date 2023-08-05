# System
import os
import logging
from copy import deepcopy
from importlib import reload

# Local
from .config import load_config
from .evaluation import evaluation
from .surrogate import surrogate

def inline_job(my_config,run_mode=0,loops=1,store_path='./'):
    """
    Execute evaluation and/or surrogate modeling directly from Python command line.

    Parameters
    ----------
    config : :class:`dict`
      Configuration settings
    run_mode : :class:`int`
      Type of job to execute. 0 for evaluation only, 1 for surrogate only, 2 for both.
    loops : :class:`int`
      Number of independent evaluation + surrogate modeling to execute sequentially.

    Examples
    ---------
    Given a specific configuration dictionary already prepared, the job can be executed as follows:

    >>> import hyppo
    >>> hyppo.inline_job(config,run_mode=2,loops=20)
    """
    for iloop in range(loops):
        if run_mode in [0,2]:
            logging.shutdown()
            reload(logging)
            config = load_config(config_file=deepcopy(my_config),operation='evaluation')
            res = evaluation(config)
        if run_mode in [1,2]:
            logging.shutdown()
            reload(logging)
            config = load_config(config_file=deepcopy(my_config),operation='surrogate')
            res = surrogate(config)
        # Store results
        if store_path!='./' or loops>1:
            log_dir = config['dist']['log_dir']
            full_path = '%s/%s/%s' % (log_dir,store_path,log_dir) if loops==1 else '%s/%s/%03i/%s' % (log_dir,store_path,iloop+1,log_dir)
            os.makedirs(full_path, exist_ok=True)
            os.system('mv %s/*.log %s' % (log_dir,full_path))
            if os.path.exists('%s/models' % log_dir):
                os.system('mv %s/models %s' % (log_dir,full_path))
