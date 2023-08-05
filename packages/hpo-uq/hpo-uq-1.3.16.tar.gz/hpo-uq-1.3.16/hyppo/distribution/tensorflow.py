import os
import tensorflow as tf

def init_workers_cpu(trainer, split):
    """Initialize workers with MPI backend"""
    if trainer=='internal' or split=='trial':
        import horovod.tensorflow as hvd
        hvd.init()
    return {
        'rank'   : int(os.environ['SLURM_PROCID']),
        'size'   : int(os.environ['SLURM_NPROCS']),
        'step'   : int(os.environ['SLURM_STEP_ID']),
        'ntasks' : int(os.environ['SLURM_NTASKS']),
    }

def init_workers_gpu(trainer, split):
    """Initialize workers with HVD backend and sync file"""
    if trainer=='internal' or split=='trial':
        import horovod.tensorflow as hvd
        hvd.init()
        gpus = tf.config.list_physical_devices("GPU")
        assert len(gpus) == int(os.environ['SLURM_NPROCS'])
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        tf.config.set_visible_devices(gpus[int(os.environ['SLURM_PROCID'])], 'GPU')
    return {
        'rank'   : int(os.environ['SLURM_PROCID']),
        'size'   : int(os.environ['SLURM_NPROCS']),
        'step'   : int(os.environ['SLURM_STEP_ID']),
        'ntasks' : int(os.environ['SLURM_NTASKS']),
    }

def init_workers(trainer, split='trial', node_type='cpu', backend=None, **kwargs):
    """Initialize workers for specified backend in Tensorflow.

    Note that only a few modes are currently supported:
    - HVD backend with ranks determined by Horovod library.
    """
    if 'SLURM_NTASKS' not in os.environ.keys():
        return {'backend':None, 'rank':0, 'size':1, 'step':0, 'ntasks':1}
    elif node_type == 'gpu':
        return init_workers_gpu(trainer, split)
    else:
        return init_workers_cpu(trainer, split)
