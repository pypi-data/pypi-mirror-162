# System
import logging

# Local
from .gp_opt import gp
from .rbf_opt import rbf

def surrogate(config,**kwargs):
    logging.info('CONFIGURATION:')
    logging.info('-'*40 + '\n\n%s\n' % config['original'])
    eval(config['hpo']['surrogate'])(
        config,**config['prms'],**config['hpo'],**config['dist']
    )
