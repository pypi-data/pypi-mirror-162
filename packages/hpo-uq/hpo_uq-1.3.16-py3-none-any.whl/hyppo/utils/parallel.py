# System
import os
import ast

# External
import numpy
import yaml
import pickle5 as pickle

# Local
from .extract import get_samples

def sbatch(config,**kwargs):
    nersc_cluster_script(config['path'],**config['dist'],**config['prms'])
    
def nersc_cluster_script(path, sbatch={}, operation=None, nsteps=1, ntasks=1,
                node_type='cpu', mem=None, module=None, conda='', cd=None, export=None, 
                no_submit=False, system='cori', nevals=None, mem_cap=20, **kwargs):
    """
    This function create automatically a SLURM script for NERSC clusters.
    
    https://docs.nersc.gov/systems/cori/#system-specification
    https://docs.nersc.gov/systems/perlmutter/system_details/#system-specification
    """
    procs = {'cori':{'cpu':{'haswell':(32,128),'knl':(68,96)},'gpu':{'gpu':(8,384)}},'perl':{'gpu':{'gpu':(4,256)},'cpu':{'cpu':(128,512)}}}
    assert system in procs.keys(), 'Cluster not recognized. Abort.'
    proc_per_node,mem_per_node = procs[system][node_type][sbatch['constraint']]
    operations = ['evaluation','surrogate'] if operation==None else [operation]
    script = open('hpo.sh','w')
    script.write('#!/bin/bash\n')
    # ----------------------------------------------
    #   Memory assessment
    # ----------------------------------------------
    if mem==None:
        node_per_job = numpy.ceil(nsteps * ntasks / proc_per_node)
        node_per_step = 1
        if node_per_job==nsteps:
            memory = '0'
        else:
            memory = '%iGB' % (node_per_job * (mem_per_node-mem_cap) / nsteps)
    elif mem<=mem_per_node-mem_cap:
        node_per_job = nsteps
        node_per_step = 1
        memory = '0'
    else:
        node_per_job = numpy.ceil(nsteps * mem / mem_per_node)
        node_per_step = numpy.ceil(mem / mem_per_node)
        memory = '%iGB' % mem
    # ----------------------------------------------
    #   SBATCH directive
    # ----------------------------------------------
    for key,value in sbatch.items():
        script.write('#SBATCH --%s %s\n'%(key,value))
    script.write('#SBATCH --nodes %i\n' % node_per_job)
    script.write('#SBATCH --ntasks %i\n' % (nsteps * ntasks) )
    if node_type=='gpu':
        script.write('#SBATCH --dependency singleton\n')
    script.write('#SBATCH --exclusive\n')
    script.write('#SBATCH --%ss-per-task 1\n' % node_type)
    script.write('#SBATCH --output %x-%j.out\n')
    script.write('#SBATCH --error %x-%j.err\n')
    # ----------------------------------------------
    #   Load modules
    # ----------------------------------------------
    script.write('module load parallel\n')
    if module!=None:
        for mod in module.split(';'):
            script.write('module load %s\n' % mod)
    if conda!='':
        script.write('conda activate %s\n' % conda)
        conda = 'conda activate %s &&' % conda
    if export!=None:
        script.write('export PYTHONPATH=$PYTHONPATH:%s\n' % export)
    # ----------------------------------------------
    #   Create sampling
    # ----------------------------------------------
    if 'evaluation' in operations:
        script.write('python $HOME/hyppo/bin/hyppo sampling %s\n' % path)
    # ----------------------------------------------
    #   Parallel SRUN command
    # ----------------------------------------------
    for operation in operations:
        slurm_steps = nevals if operation=='evaluation' and nevals<nsteps else nsteps
        parallel = 'parallel --delay .2 -j %i' % slurm_steps
        srun = 'srun --exclusive --nodes %i --ntasks %i' % (node_per_step,ntasks)
        if node_type=='gpu':
            srun += ' --gpus-per-task 1 --gpu-bind=none'
        else:
            srun += ' --cpus-per-task 1 --mem=%s --gres=craynetwork:0' % memory
        hpo = 'python $HOME/hyppo/bin/hyppo %s %s' % (operation,path)
        script.write('%s "%s %s %s && echo {1}" ::: {0..%i}\n' % (parallel, conda, srun, hpo, slurm_steps-1))
    script.close()
    if not no_submit:
        os.system('sbatch hpo.sh')
