# System
import os
import ast
import glob
import math
import logging

# External
import yaml
import numpy
import pandas as pd
import pickle5 as pickle
from scipy import interpolate

# Local
from ..datasets import get_data, get_loader
from ..hyperparams import get_hyperprms
from ..dnnmodels import inference

def single_convergence(solutions):
    loss_surr, sdev_surr = [], []
    for i in range(len(solutions)):
        if len(loss_surr)==0 or solutions.iloc[i].loss<loss_surr[-1]:
            loss_surr.append(solutions.iloc[i].loss)
            sdev_surr.append(solutions.iloc[i].stdev)
        else:
            loss_surr.append(loss_surr[-1])
            sdev_surr.append(sdev_surr[-1])
    return numpy.array(loss_surr), numpy.array(sdev_surr)

def mult_convergence(search_dir,with_surrogate=True,werr=False,niters=None,nruns=None,debug=False,median=False,**kwargs):
    dir_list = sorted(glob.glob(search_dir+'/*'))
    if any('.log' in dir_name for dir_name in dir_list):
        dir_list = [search_dir]
    else:
        dir_list = [os.path.join(dir_name,'logs') for dir_name in dir_list]
    n = 0
    all_results = [[],[]]
    for dir_name in dir_list:
        if os.path.isdir(dir_name)==False:
            continue
        if nruns!=None and n==nruns:
            break
        log_files = '%s/evaluation*_01.log' % dir_name
        if debug:
            print('Searching',log_files)
        evaluation = extract(log_files,debug=debug,**kwargs).sort_values(by=['nevals'])#.to_numpy()[:,1:3]
        if with_surrogate:
            surrogate  = extract(log_files.replace('evaluation','surrogate'),debug=debug,**kwargs).sort_values(by=['nevals'])#.to_numpy()[:,1:3]
            evaluation = pd.concat([evaluation,surrogate])
        loss_surr, sdev_surr = single_convergence(evaluation)
        all_results[0].append(loss_surr)
        all_results[1].append(sdev_surr)
        n+=1
    assert len(all_results[0])>0, 'No results found. Abort.'
    nevals = [len(results) for results in all_results[0]]
    niters = min(nevals) if niters==None or niters>min(nevals) else niters
    for i in range(len(all_results[0])):
        all_results[0][i] = all_results[0][i][:niters]
        all_results[1][i] = all_results[1][i][:niters]
    all_results = numpy.array(all_results)
    if median:
        mean_loss = numpy.median(all_results[0],axis=0)
    else:
        mean_loss = numpy.mean(all_results[0],axis=0)
    if werr:
        mean_sdev = numpy.sqrt(numpy.sum(all_results[1]**2,axis=0))/all_results[0].shape[0]
    else:
        mean_sdev = numpy.std(all_results[0],axis=0)
    return mean_loss, mean_sdev

def extract(path,target_loss='inner',target_unc='Uncertainty',debug=False,raw=False,**kwargs):
    hps = []
    data = []
    nevals = 0
    for fname in sorted(glob.glob(path)):
        if debug:
            print('Extract results from',fname)
        network_names, network_prms = [], []
        content = numpy.loadtxt(fname,dtype=str,delimiter='\n')
        for i,line in enumerate(content):
            if 'CONFIGURATION:' in line:
                cfg = ast.literal_eval(content[i+2].strip())
                names = cfg['prms']['names']
                mult = cfg['prms']['mult']
            if 'Samples:' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [int(k) for k in samples.split()]
                if raw:
                    names = ['hp%i'%(i+1) for i in range(len(samples))]
                else:
                    samples = [int(samples[n])*mult[n] for n in range(len(mult))]
                network_prms = []
            if 'parameters in' in line:
                network_names.append(line.split()[-1])
                network_prms.append(int(line.split()[-4].replace(',','')))
            if 'Number of parameters :' in line:
                network_names.append('tot_prms')
                network_prms.append(int(line.split()[-1].replace(',','')))
            if '%s Loss' % target_loss.capitalize() in line:
                loss = float(line.split()[-1])
            if 'EVALUATION' in line:
                nevals = int(line.split()[-3])
            if 'Total of sample sets used' in line:
                nevals = int(line.split()[-1])+1
            if target_unc in line:
                n_sizes = len(numpy.unique(network_names))
                std = float(line.split()[-1])
                time = float(content[i+2].split()[-2])
                data.append([loss,std]+network_prms[:n_sizes]+samples+[nevals,time])
                hps.append(samples)
            if 'Lower Bound of CI' in line:
                n_sizes = len(numpy.unique(network_names))
                std = loss-float(line.split()[-1])
                time = float(content[i+2].split()[-2])
                data.append([loss,std]+network_prms[:n_sizes]+samples+[nevals,time])
                hps.append(samples)
    if len(data)!=len(numpy.unique(hps,axis=0)):
        print('WARNING: Some hyperparameter sets were evaluated more than once in %s (%i/%i)' % (path,len(numpy.unique(hps,axis=0)),len(data)))
    if len(data)>0:
        indexes = numpy.unique(network_names, return_index=True)[1]
        network_names = [network_names[index] for index in sorted(indexes)]
        data = pd.DataFrame(data=data,columns=['loss','stdev']+network_names+names+['nevals','time']).sort_values(by=['nevals'])
        # Ensuring that index is unique
        data.nevals = numpy.arange(len(data))
    if debug:
        print(data)
    return data

def extract_trials(path,debug=False,**kwargs):
    data = []
    nevals = 0
    for fname in sorted(glob.glob(path)):
        if debug:
            print('Extract results from',fname)
        params, gen_params, dis_params = float('nan'), float('nan'), float('nan')
        content = numpy.loadtxt(fname,dtype=str,delimiter='\n')
        for i,line in enumerate(content):
            if 'Samples:' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [int(k) for k in samples.split()]
                network_names, network_prms = [], []
            if 'parameters in' in line:
                network_names.append(line.split()[-1])
                network_prms.append(int(line.split()[-4].replace(',','')))
            if 'Number of parameters :' in line:
                network_names.append('tot_prms')
                network_prms.append(int(line.split()[-1].replace(',','')))
            if 'TRIAL ' in line:
                trial = int(line.split()[-4])
            if 'EVALUATION' in line:
                nevals = int(line.split()[-3])
            if 'Total of sample sets used' in line:
                nevals = int(line.split()[-1])+1
            if 'Test Loss' in line:
                loss = float(line.split()[-1])
                time = float(content[i+1].split()[-2])
                data.append([loss,trial]+network_prms+samples+[nevals,time])
    if len(data)>0:
        data = pd.DataFrame(data=data,columns=['loss','trial']+network_names+['hp%i'%(i+1) for i in range(len(samples))]+['nevals','time']).sort_values(by=['nevals'])
    if debug:
        print(data)
    return data

def check_surrogate_sample(log_dir,step,iloop):
    samples = []
    log_file = './%s/surrogate_%03i_01.log' % (log_dir,step+1)
    if os.path.exists(log_file):
        while True:
            try:
                log_content = numpy.loadtxt(log_file,dtype=str,delimiter='\n').tolist()
                break
            except:
                pass
        for i,line in enumerate(log_content):
            if 'SURROGATE ITERATION' in line:
                isurrogate = int(line.split()[-3])
            if 'Samples:' in line and isurrogate==iloop+1:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = numpy.array([k for k in samples.split()],dtype=int)
                break
    return samples

def check_evaluation_outer_loss(target,output,log_dir,step,**kwargs):
    outer_loss = False
    log_file = './%s/%s_%03i_01.log' % (log_dir,output.split('_')[0],step+1)
    if os.path.exists(log_file):
        while True:
            try:
                log_content = numpy.loadtxt(log_file,dtype=str,delimiter='\n').tolist()
                break
            except:
                pass
        for i,line in enumerate(log_content):
            if 'Samples:' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [int(k) for k in samples.split()]
            if 'Outer Loss' in line and list(samples)==list(target):
                outer_loss = True
                break
    return outer_loss

def gather_trials(target,output,log_dir,ntasks,step,trial,split,**kwargs):
    """
    Collect trial losses for given sample set.
    
    Parameters
    ----------
    results : :class:`dict`
      Results
    """
    if split=='trial':
        losses = numpy.zeros((trial,1))
    else:
        losses = numpy.zeros((trial,ntasks))
    n=0
    for rank in range(ntasks):
        log_file = './%s/%s_%03i_%02i.log' % (log_dir,output.split('_')[0],step+1,rank+1)
        while True:
            try:
                log_content = numpy.loadtxt(log_file,dtype=str,delimiter='\n').tolist()
                break
            except:
                pass
        for i,line in enumerate(log_content):
            if 'Samples:' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [int(k) for k in samples.split()]
            if 'TESTING' in line and list(samples)==list(target):
                itrial = int(line.split()[-4])-1
                for sub_line in log_content[i:]:
                    if 'Test Loss' in sub_line and list(samples)==list(target):
                        loss = float(sub_line.split()[-1])
                        if split=='trial':
                            losses[itrial,0] = loss
                        else:
                            losses[itrial,rank] = loss
                        break
    losses = [] if 0 in losses else numpy.mean(losses,axis=1)
    return losses

def extract_evals(log_dir,**kwargs):
    uq = False
    all_sets, samples, fvals, uqvals = [], [], [], []
    for file_name in sorted(glob.glob('%s/*.log' % log_dir)):
        file_content = numpy.loadtxt(file_name,dtype=str,delimiter='\n').tolist()
        for i,line in enumerate(file_content):
            if 'Samples:' in line:
                sample_set = line.split('Samples:')[-1].strip()[1:-1]
                sample_set = [int(k) for k in sample_set.split()]
                all_sets.append(sample_set)
            if 'UNCERTAINTY QUANTIFICATION' in line:
                uq = True
            if 'Outer Loss' in line:
                loss = float(line.split()[-1])
                if math.isnan(loss)==False:
                    fvals.append(loss)
                    samples.append(sample_set)
                    if uq:
                        unc = float(file_content[i+2].split()[-1])
                        uqvals.append([loss-2*unc,loss+2*unc])
    all_sets = numpy.unique(all_sets,axis=0)
    samples = numpy.array(samples,dtype=int)
    logging.info('finding parameter sets : %i / %i' % (len(all_sets),len(samples)))
    assert len(samples)>0, 'No samples found for surrogate modeling. Abort.'
    fvals = numpy.array(fvals).reshape(-1,1)
    if len(uqvals)>0:
        fvals = numpy.hstack((fvals,uqvals))
    # Initialize best point found so far = first evaluated point
    imin = numpy.where(fvals[:,0]==min(fvals[:,0]))[0][0]
    Fbest = fvals[imin,0]
    xbest = samples[imin]
    return samples, fvals, Fbest, xbest, all_sets

def get_samples(log_path,surrogate=False,mult=False):
    all_samples = {}
    evaluations = []
    logs = glob.glob(log_path+'/*.log')
    for file_name in logs:
        file_content = numpy.loadtxt(file_name,delimiter='\n',dtype=str)
        for i,line in enumerate(file_content):
            if 'CONFIGURATION:' in line:
                config = ast.literal_eval(file_content[i+2].strip())
                for key in ['names','mult','xlow','xup']:
                    all_samples[key] = config['prms'][key]
            if 'EVALUATION' in line:
                evaluations.append([int(line.split()[-3])-1])
            if 'Samples:' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [int(k) for k in samples.split()]
                if mult:
                    evaluations[-1] += [a*b for a,b in zip(samples,all_samples['mult'])]
                else:
                    evaluations[-1] += samples
            if 'Outer Loss' in line:
                evaluations[-1] += [float(line.split()[-1])]
            if 'Lower Bound of CI' in line:
                evaluations[-1] += [float(line.split()[-1])]
            if 'Upper Bound of CI' in line:
                evaluations[-1] += [float(line.split()[-1])]
            if 'Execution Time' in line:
                evaluations[-1] += [float(line.split()[-2])]
    evaluations = numpy.array(evaluations,ndmin=2)
    idxs = numpy.argsort(numpy.array(evaluations)[:,0])
    all_samples['evals'] = numpy.array(evaluations)[idxs,1:]
    if surrogate:
        surrogate = []
        for line in open(log_path+'/surrogate.log'):
            if 'OPTIMIZATION' in line:
                surrogate.append([int(line.split()[-3])-1])
            if 'Samples' in line:
                samples = line.split('Samples:')[-1].strip()[1:-1]
                samples = [float(k) for k in samples.split()]
                if mult:
                    surrogate[-1] += [a*b for a,b in zip(samples,all_samples['mult'])]
                else:
                    surrogate[-1] += samples
            if 'Outer Loss' in line:
                surrogate[-1] += [float(line.split()[-1])]
            if 'Lower Bound of CI' in line:
                surrogate[-1] += [float(line.split()[-1])]
            if 'Upper Bound of CI' in line:
                surrogate[-1] += [float(line.split()[-1])]
            if 'Execution Time' in line:
                surrogate[-1] += [float(line.split()[-2])]
        #surrogate = numpy.array(surrogate[:-1])
        surrogate = numpy.array(surrogate)
        idxs = numpy.argsort(surrogate[:,0])
        all_samples['sgate'] = surrogate[idxs,1:]
    return all_samples

def data_and_model(path_to_config,samples,**kwargs):
    with open(path_to_config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    data = get_data(**config['model'],**config['data'])
    samples = ['%i'%samples['hp%i'%(i+1)] for i in range(len(config['prms']['names']))]
    x_sc = {name:mult*int(sample) for name,mult,sample in zip(config['prms']['names'],config['prms']['mult'],samples)}
    if 'default' in config['prms'].keys() and type(config['prms']['default'])==dict:
        x_sc = {**x_sc,**config['prms']['default']}
    hyperprms = get_hyperprms(config['trainer'], x_sc, **config['model'])
    loaders = get_loader(data, **hyperprms, **config['model'])
    preds = []
    for i in range(config['model']['trial']):
        out = 'evaluation_%s/%02i' % ('_'.join(samples),i+1)
        y_real, y_pred = inference(data=loaders,hyperprms=hyperprms,log_dir=os.path.dirname(path_to_config)+'/logs',output=out,**config['model'])
        y_real = y_real.detach().numpy().squeeze()
        preds.append(y_pred.detach().numpy().squeeze())
    return y_real, numpy.array(preds)

def make_tables(table_type='evaluation'):
    os.makedirs('tables',exist_ok=True)
    if table_type == 'evaluation':
        data = get_samples('logs/')
        f = open('tables/evaluation.txt',"w+")
    else:
        data = get_samples('logs/',surrogate=True)
        f = open('tables/hpo_table.txt',"w+")
    evals = data['evals']
    hps = str([ i for i in data['names']])
    num_prms = len(data['names'])
    for i in range(num_prms):
        evals[:,i] = data['mult'][i]*evals[:,i]
        if 'sgate' in data:
            data['sgate'][:,i] = data['mult'][i]*data['sgate'][:,i]
    f.write('\\begin{table}[h!]\n')
    if numpy.shape(evals)[1] > num_prms+2:
        f.write('\\begin{tabular}{|c|c|c|c|c|c|}\\hline\n')
        f.write('\\textbf{Iterations} & \\textbf{HPs:'+hps+'} & \\textbf{Mean Objective Value} & \\textbf{Lower Bound of C.I.} &\\textbf{Upper Bound of C.I.} &\\textbf{Time (s)} \\\\ \\hline \n')
        for i in range(numpy.shape(evals)[0]):
            f.write('Eval. {}&{}&{}&{}&{}&{}\\\\ \\hline \n'.format(i+1,evals[i,0:num_prms],evals[i,num_prms],evals[i,num_prms+1],evals[i,num_prms+2],evals[i,-1]))
        if 'sgate' in data:
            s_evals = data['sgate']
            for i in range(numpy.shape(s_evals)[0]):
                f.write('HPO. {}&{}&{}&{}&{}&{}\\\\ \\hline \n'.format(i+1,s_evals[i,0:num_prms],s_evals[i,num_prms],s_evals[i,num_prms+1],s_evals[i,num_prms+2],s_evals[i,-1]))
    else:
        f.write('\\begin{tabular}{|c|c|c|c|}\\hline\n')
        f.write('\\textbf{Iterations} & \\textbf{HPs:'+hps+'} & \\textbf{Objective Value} & \\textbf{Time (s)} \\\\ \\hline \n')
        for i in range(numpy.shape(evals)[0]):
            f.write('Eval. {}&{}&{}&{}\\\\ \\hline \n'.format(i+1,evals[i,0:num_prms],evals[i,num_prms],evals[i,-1]))
        if 'sgate' in data:
            s_evals = data['sgate']
            for i in range(numpy.shape(s_evals)[0]):
                f.write('HPO. {}&{}&{}&{}\\\\ \\hline \n'.format(i+1,s_evals[i,0:num_prms],s_evals[i,num_prms],s_evals[i,-1]))
    f.write('\\end{tabular} \n')
    f.write('\\end{table}')
    f.close()

# def get_loss(log_path,weight=False,grid=False,nepochs=50,verbose=False,all_losses=False):
#     if os.path.isfile(log_path):
#         logs = [log_path]
#     else:
#         log_path = os.path.join(log_path,'out_*.log')
#         logs = glob.glob(log_path)
#     trials = []
#     losses = []
#     results = numpy.empty((0,5))
#     for i,file_name in enumerate(logs):
#         for line in open(file_name):
#             if 'Evaluation' in line:
#                 if len(trials)>0 and verbose:
#                     print('Trials not reset, something wrong in file %s'%logs[i-1])
#                 trials = []
#                 neval = int(line.split()[-1])
#             if 'Hyperparameters' in line:
#                 hyperprms = ast.literal_eval(line.split('Hyperparameters:')[-1].strip())
#                 epochs = hyperprms['epochs']
#                 nodes = hyperprms['nodes'][0]#*hyperprms['nodes'][0]
#                 norm = epochs/nodes
#             if 'TRIAL' in line:
#                 ntrials = int(line.split()[-1].split('/')[-1])
#             if 'Epoch ' in line:
#                 nepoch = int(line.split()[4].split('/')[0])
#                 if nepoch==epochs:
#                     loss = float(line.split()[-1])
#                     trials.append(loss)
#             if 'Testing' in line:
#                 losses.extend(trials)
#                 loss = numpy.median(trials)
#                 sdev = numpy.std(trials)
#                 if weight: loss *= norm
#                 results = numpy.vstack((results,[neval,epochs,nodes,loss,sdev]))
#                 trials = []
#     results = results[numpy.argsort(results[:,0])]
#     (x,y,z,e) = results[:,1:].T
#     if grid:
#         # print('Loss: min %.5f | med %.5f max %.2E'%(numpy.nanmin(z),numpy.median(z),numpy.nanmax(z)))
#         xi = numpy.arange(1,nepochs+1)
#         yi = numpy.arange(1,max(y)+1)
#         xi,yi = numpy.meshgrid(xi,yi)
#         z = interpolate.griddata((x,y),z,(xi,yi),method='linear')
#         e = interpolate.griddata((x,y),e,(xi,yi),method='linear')
#     return losses if all_losses else (x,y,z,e)

# def get_sensitivity(samples):
#     from SALib.analyze import morris
#     mult = samples['mult']
#     xlow = samples['xlow']
#     xup = samples['xup']
#     problem = {
#         'num_vars': len(samples['names']),
#         'names': samples['names'],
#         'bounds': numpy.array([[i*j for i,j in zip(xlow,mult)],
#                                [i*j for i,j in zip(xup,mult)]]).T
#     }
#     n_samples = (1+len(samples['names']))*(len(samples['evals'])//(1+len(samples['names'])))
#     X = samples['evals'][:n_samples,:len(samples['names'])]
#     Y = samples['evals'][:n_samples,-1]
#     sensitivity = morris.analyze(problem, X, Y)
#     return sensitivity

# def get_sensitivity_from_tensorboard(log_dir):
#     from SALib.sample import saltelli
#     from SALib.analyze import sobol
#     from SALib.test_functions import Ishigami
#     import tensorflow.compat.v1 as tf
#     from collections import defaultdict
#     logs = glob.glob(log_dir+'/evaluation_*/logs/*/*/events.out.tfevents.*.v2')
#     metrics = defaultdict(list)
#     for file_name in logs:
#         for e in tf.train.summary_iterator(file_name):
#             for v in e.summary.value:
#                 if isinstance(v.simple_value, float):
#                     metrics[v.tag].append(v.simple_value)
#     print(metrics)
    
# def conv2surf(samples,names=[]):
#     assert len(names)==2, 'Exactly two parameters must be selected for 3D plotting. Abort.'
#     # Identify index for each selected parameters
#     xi = samples['names'].index(names[0])
#     yi = samples['names'].index(names[1])
#     # Create data grid
#     xvals = numpy.arange(samples['xlow'][xi],samples['xup'][xi]+1,1) * samples['mult'][xi]
#     yvals = numpy.arange(samples['xlow'][yi],samples['xup'][yi]+1,1) * samples['mult'][yi]
#     # Interpolate model with existed sparse data
# #     f = interpolate.interp2d(samples['evals'][:,xi], samples['evals'][:,yi], samples['evals'][:,-1], kind='linear')
#     x,y,z = samples['evals'][:,xi], samples['evals'][:,yi], samples['evals'][:,-1]
#     # print('Loss: min %.5f | med %.5f max %.2E'%(numpy.nanmin(z),numpy.median(z),numpy.nanmax(z)))
#     xi,yi = numpy.meshgrid(xvals,yvals)
#     z = interpolate.griddata((x,y),z,(xi,yi),method='linear')
#     return xvals, yvals, z
