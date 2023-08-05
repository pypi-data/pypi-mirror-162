"""
Logging functionality for printing to stdout, log file, etc.
"""

# System imports
import os
import sys
import logging
import logging.config

def create_logging(operation,verbose=False,log_dir='logs',step=0,nsteps=1,node_type='cpu',rank=0,size=1,**kwargs):
    os.makedirs(log_dir,exist_ok=True)
    log_file = './%s/%s_%03i_%02i.log' % (log_dir,operation,step+1,rank+1)
    config_logging(verbose=verbose,log_file=log_file)
    # Print out parallelization setup in log file
    logging.info('='*40)
    logging.info('DISTRIBUTION:')
    logging.info('-'*40)
    if 'SLURM_JOB_ID' in os.environ.keys():
        logging.info('\tParallel step {} / {}'.format(step+1,nsteps))
        logging.info('\tJob utilizes {} {} nodes:'.format(os.environ['SLURM_JOB_NUM_NODES'],node_type.upper()))
        logging.info('\t\t{}'.format(os.environ['SLURM_JOB_NODELIST']))
        logging.info('\tStep utilizes {} {} nodes:'.format(os.environ['SLURM_STEP_NUM_NODES'],node_type.upper()))
        logging.info('\t\t{}'.format(os.environ['SLURM_STEP_NODELIST']))
        logging.info('\tTask executes on {}:'.format(os.environ['SLURMD_NODENAME']))
        logging.info('\t\t{} rank is {}'.format(node_type.upper(),rank))
        logging.info('\t\t{} size is {}'.format(node_type.upper(),size))
    else:
        logging.info('\tExecuting step {} / {}'.format(step+1,nsteps))
        logging.info('\t\t{} rank is {}'.format(node_type.upper(),rank))
        logging.info('\t\t{} size is {}'.format(node_type.upper(),size))
    logging.info('='*40+'\n')

def config_logging(verbose, log_file=None):
    logging.config.dictConfig({'version':1,'disable_existing_loggers': True})
    log_format = '%(asctime)s %(levelname)s %(message)s'
    log_level = logging.DEBUG if verbose else logging.INFO
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    handlers = [stream_handler]
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    logging.basicConfig(level=log_level, format=log_format, handlers=handlers)

