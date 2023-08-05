# System
import os

# External
import torch
import torch.distributed as dist

def _get_sync_file():
    """Logic for naming sync file using slurm env variables"""
    sync_file_dir = '%s/pytorch-sync-files' % os.environ['SCRATCH']
    os.makedirs(sync_file_dir, exist_ok=True)
    sync_file = 'file://%s/pytorch_sync.%s.%s' % (
        sync_file_dir, os.environ['SLURM_JOB_ID'], os.environ['SLURM_STEP_ID'])
    return sync_file

def init_workers_gloo_file():
    """Initialize workers with GLOO backend and sync file"""
    rank = int(os.environ['SLURM_PROCID'])
    n_ranks = int(os.environ['SLURM_NPROCS'])
    sync_file = _get_sync_file()
    dist.init_process_group(backend='gloo', world_size=n_ranks, rank=rank,
                            init_method=sync_file)
    return {
        'rank'       : rank,
        'size'       : n_ranks,
        'device'     : torch.device('cuda',rank),
        'device_ids' : [rank],
        'step'       : int(os.environ['SLURM_STEP_ID']),
        'ntasks'     : int(os.environ['SLURM_NTASKS']),
    }

def init_workers_nccl_file():
    """Initialize workers with NCCL backend and sync file"""
    rank = int(os.environ['SLURM_PROCID'])
    n_ranks = int(os.environ['SLURM_NPROCS'])
    sync_file = _get_sync_file()
    print('Setting up with sync file', sync_file)
    dist.init_process_group(backend='nccl', world_size=n_ranks, rank=rank,
                            init_method=sync_file)
    return {
        'rank'       : rank,
        'size'       : n_ranks,
        'device'     : torch.device('cuda',rank),
        'device_ids' : [rank],
        'step'       : int(os.environ['SLURM_STEP_ID']),
        'ntasks'     : int(os.environ['SLURM_NTASKS']),
    }

def init_workers_mpi():
    """Initialize workers with MPI backend"""
    dist.init_process_group(backend='mpi')
    return {
        'rank'       : dist.get_rank(),
        'size'       : dist.get_world_size(),
        'device'     : torch.device('cpu'),
        'device_ids' : [],
        'step'       : int(os.environ['SLURM_STEP_ID']),
        'ntasks'     : int(os.environ['SLURM_NTASKS']),
    }

def init_workers(trainer, backend=None, **kwargs):
    """Initialize workers for specified backend.
    
    Note that only a few modes are currently supported:
    - MPI backend
    - NCCL backend with ranks determined by SLURM variables and intialized via
      shared file under $SCRATCH.
    - GLOO backend with rank determined by SLURM variables and intialized via
      shared file under $SCRATCH.
    
    Returns
    -------
    rank : :class:`int`
      Current MPI rank
    n_ranks : :class:`int`
      Size of parallel processes
    device : :class:`torch.device`
      Type of processor device
    device_ids : :class:`int`
      Current device ID, is None if CPU processor, otherwise [rank] if GPU
    """
    if 'SLURM_NTASKS' not in os.environ.keys():
        return {
            'backend'    : None,
            'rank'       : 0,
            'size'       : 1,
            'device'     : torch.device('cpu'),
            'device_ids' : [],
            'step'       : 0,
            'ntasks'     : 1,
        }
    elif backend == 'mpi':
        return init_workers_mpi()
    elif backend == 'nccl':
        return init_workers_nccl_file()
    elif backend == 'gloo':
        return init_workers_gloo_file()
    else:
        return {
            'rank'       : 0,
            'size'       : 1,
            'device'     : torch.device('cpu'),
            'device_ids' : [],
            'step'       : int(os.environ['SLURM_STEP_ID']),
            'ntasks'     : int(os.environ['SLURM_NTASKS']),
        }
