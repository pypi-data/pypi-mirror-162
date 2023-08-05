# System
import os

# External
import yaml

# Local
from .datasets import get_data
from .distribution import get_workers
from .utils import create_logging

def load_config(config_file=None,debug=0,verbose=False,operation=None,no_submit=False,log_dir='logs',**kwargs):
    """
    Load configuration file and embed relevant parameters and data in dictionary.
    """
    # Load configuration file
    if type(config_file)==str:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        config['path'] = config_file#os.path.abspath(config_file)
    else:
        config = config_file
        config['path'] = None
    config['original'] = str(config)
    # Add empty model section if absent and check ML library
    if 'model' not in config.keys():
        config['model'] = {}
    elif config['trainer']=='internal':
        assert 'library' in config['model'].keys(), \
        'ML library must be specified in configuration file for internal trainer. Abort.'
        config['model']['debug'] = debug
    if 'trial' not in config['model'].keys():
        config['model']['trial'] = 1
    # Update dist section
    default = {
        'step':0,
        'nsteps':1,
        'ntasks':1,
        'node_type':'cpu',
        'backend':None,
        'split':'trial',
        'log_dir':log_dir,
        'no_submit':no_submit,
        'system':'cori',
    }
    if 'dist' in config.keys() and 'log_dir' in config['dist'].keys():
        log_dir = config['dist']['log_dir']
    if 'SLURM_NTASKS' in os.environ.keys() or operation=='sbatch':
        assert 'dist' in config.keys(), 'Distribution settings not defined. Abort.'
        config['dist'] = {**default,**config['dist']}
    else:
        config['dist'] = {**default,**{'log_dir':log_dir}}
    # Initialize workers and prepare data
    if operation in ['evaluation','surrogate']:
        config['dist'] = {**config['dist'],**get_workers(**config)}
        config['dist'].pop('operation', None)
        create_logging(operation,verbose,**config['dist'])
        # Extract training and test datasets
        if 'data' in config.keys():
            # Merging needed to avoid duplicate (e.g. verbose)
            dicts = {**config['model'],**config['data']}
            data = get_data(**dicts)
            config['data'] = {**config['data'], **data}
    return config
