# System
import os
import time
import copy
import random
import logging
import importlib

# External
import torch
import numpy
import scipy
from scipy.stats import norm
from scipy.integrate import quad
import matplotlib.pyplot as plt

# Local
from .utils import load_model

def uq_quantifier(trainer, trials=None, uq_weights=[0.5,0.5], dropout_masks=30, data_noise=0, device=None, **kwargs):
    """
    Main Uncertainty Quantification (UQ) algorithm.
    """
    T = len(trials)
    N = dropout_masks
    uq_obj_vals = []
    uq_means = {'trained':{}, 'Unc':{}}
    # uq_vars  = {'trained':{}, 'Unc':{}}
    architecture = copy.deepcopy(trainer.model)
    for j in range(T):
        # Load saved model
        path = os.path.join(trainer.checkpoint_dir,'%02i'%(j+1),'model.pt')
        trainer.model = load_model(path,architecture,device)
        if data_noise > 0.0:
            trainer.model = ADF_Dropout_Model_Builder(trainer.model,data_noise,True)
        # Run prediction evaluation
        logging.debug('  Prediction evaluation')
        trainer.model.eval()
        trained_val = trainer.evaluate(test=True,**kwargs)
        trained_pred, y_real = trainer.y_pred, trainer.y_real
        uq_means['trained'][j] = numpy.asarray(trained_pred.cpu().detach().numpy())
        # Adapt model for MC Dropout
        logging.debug('-'*40)
        logging.debug('UQ results on model %i/%i:' % (j+1,T))
        if data_noise == 0.0:
            logging.debug('Applying Dropout Model Builder to model %i' % (j+1))
            trainer.model = Dropout_Model_Builder(trainer.model)
        else:
            logging.debug('Applying ADF Dropout Model Builder to model %i' % (j+1))
            trainer.model = ADF_Dropout_Model_Builder(trainer.model,data_noise)
        # Run Monte Carlo dropout
        model_vals = []
        model_vals.append(trained_val)
        # uq_vars['trained'][j]  = numpy.asarray(trained_var)
        trainer.model.train()
        start_time = time.time()
        for t in range(N): 
            logging.debug('  Dropout mask %i/%i' % (t+1,N))
            val = trainer.evaluate(test=True,**kwargs)
            pred, y_real = trainer.y_pred, trainer.y_real
            model_vals.append(val)
            uq_means['Unc'][j*N+t] = numpy.asarray(pred.cpu().detach().numpy())
            # uq_vars['Unc'][j*N+t] = numpy.asarray(pred_var)
        logging.debug('-'*40)
        logging.info('Model {:>2} | Loss {:>8.5f} | {:>10.3f} s'.format(j+1,numpy.nanmean(torch.stack(model_vals).cpu().detach().numpy()),time.time()-start_time))
        uq_obj_vals.extend(model_vals)
    pred_mean = (uq_weights[0]/T)*sum(uq_means['trained'].values())+uq_weights[1]*sum(uq_means['Unc'].values())/(T*N)
    save_results(T,N,uq_weights,uq_means,pred_mean,y_real,**kwargs)
    pred_mean_obj_val = trainer.criterion(torch.tensor(pred_mean).cpu(),y_real.cpu())
    pred_std = numpy.std(torch.stack(uq_obj_vals).cpu().detach().numpy())
    return pred_mean_obj_val, pred_std

#-------------------------------------------------------------------------------------------
# These classes construct the layers which propogate data uncertainty using ADF
#-------------------------------------------------------------------------------------------
class ADF_Linear_Layer(torch.nn.Module):
    def __init__(self,Linear):
        super(ADF_Linear_Layer, self).__init__()
        self.W = Linear.weight.detach()
        self.b = Linear.bias.detach()        
    def forward(self, X):
        term_1 = torch.matmul(self.W,X[0,:].T.float()).T
        term_2 = torch.reshape(self.b,term_1.size())
        X_out = torch.zeros((2,term_1.size(0)))
        X_out[0,:] = term_1 + term_2
        X_out[1,:] = torch.matmul((self.W*self.W),X[1,:].T.float()).T
        return X_out
    
class ADF_Dropout_Layer(torch.nn.Module):
    def __init__(self,dropout_rate):
        super(ADF_Dropout_Layer, self).__init__()
        self.p = dropout_rate     
    def forward(self, X):
        X_out = torch.zeros(X.size())
        drop_vec = torch.tensor(numpy.random.binomial(1,1-self.p,X.size(1)))
        X_out[0,:] = drop_vec*X[0,:]*(1/(1-self.p))
        X_out[1,:] = drop_vec*X[1,:]*(1/(1-self.p))
        return X_out
    
class ADF_ReLU_Layer(torch.nn.Module):
    def __init__(self):
        super(ADF_ReLU_Layer,self).__init__()
    def forward(self,X):
        X_out = torch.zeros(X.size())
        x = X[0,:]
        y = X[1,:]
        sigma   = torch.sqrt(torch.abs(y))
        sigma[torch.where(torch.abs(sigma)<1e-10)]=0.0 # deals with numerical round-off
        ratio   = x/sigma
        x_new = x*norm.cdf(ratio) + sigma*norm.pdf(ratio)
        y_new = (x**2 + y)*norm.cdf(ratio) + x*sigma*norm.pdf(ratio) - x_new**2
        y_new[torch.where(y_new<.0)]=0.0 # deals with numerical round-off
        X_out[0,:] = x_new
        X_out[1,:] = y_new
        return X_out
    
class ADF_Other_Act_Layer(torch.nn.Module):
    def __init__(self,layer_name):
        super(ADF_Other_Act_Layer,self).__init__()
        self.name = layer_name
    def forward(self,X):
        torch_act={'Softmax': torch.nn.Softmax,'Tanh': torch.nn.Tanh,'ELU': torch.nn.ELU,'SELU': torch.nn.SELU,\
            'Softplus': torch.nn.Softplus,'Softsign': torch.nn.Softsign,'Sigmoid': torch.nn.Sigmoid,'Hardsigmoid': torch.nn.Hardsigmoid}
        X_out = torch.zeros(X.size())
        in_mean = X[0,:]
        in_std = torch.sqrt(X[1,:])
        if self.name in torch_act:
            f = lambda x,mean,std: torch_act[self.name]()(torch.tensor(x))*norm.pdf((x-mean)/std)/std
            g = lambda x,mean,std: (torch_act[self.name]()(torch.tensor(x))**2)*norm.pdf((x-mean)/std)/std
        out_mean=[]
        out_var =[]
        for i in range(X.size(1)):
            out_1,err_1 = quad(f, -numpy.inf, numpy.inf, args=(in_mean[i],in_std[i]), limit=150, epsabs=1e-6)
            out_2,err_2 = quad(g, -numpy.inf, numpy.inf, args=(in_mean[i],in_std[i]), limit=150, epsabs=1e-6)
            out_var.append(-out_1**2 + out_2)
            out_mean.append(out_1)
        out_mean = torch.tensor(out_mean)
        out_var  = torch.tensor(out_var)
        X_out[0,:] = out_mean
        X_out[1,:] = out_var
        return X_out

def adf_layer_selector(model, lay_num, lay_name, dropout_rate):
    if lay_name == 'Linear':
        layer = ADF_Linear_Layer(model.layers[lay_num])
    elif lay_name == 'Dropout':
        layer = ADF_Dropout_Layer(dropout_rate)
    elif lay_name == 'ReLU':
        layer = ADF_ReLU_Layer()
    else:
        layer = ADF_Other_Act_Layer(lay_name)
    return layer

class ADF_Dropout_Model_Builder(torch.nn.Module):
    
    def __init__(self, model, data_noise, exact = False):
        super(ADF_Dropout_Model_Builder, self).__init__()
        self.in_size = model.prop['input_size']
        self.out_shape = model.prop['output_shape']
        self.noise = data_noise
        lay_names = []
        for i in range(len(model.layers)):
            lay_names.append(repr(type(model.layers[i])).split(".")[-1].split("'")[0])
        if 'Dropout' in lay_names:
            indx = lay_names.index('Dropout')
            p_drop = model.layers[indx].p
            drop_in = True
        elif exact:
            p_drop = 0.0
            drop_in = False
        else:
            p_drop = 0.05 # This the default dropout rate for the dropout masks
            drop_in = False
        layers = []
        for i in range(len(model.layers)):
            if drop_in:
                layers.append(adf_layer_selector(model, i, lay_names[i], p_drop))
            else:
                if lay_names[i] == 'Linear':
                    layers.append(adf_layer_selector(model, i, lay_names[i], p_drop))
                else:
                    layers.append(adf_layer_selector(model, i, lay_names[i], p_drop))
                    layers.append(adf_layer_selector(model, i,'Dropout', p_drop))
        self.layers = torch.nn.Sequential(*layers)
        
    def forward(self,data):
        data = data.reshape(data.shape[0],self.in_size)
        out_mean = torch.zeros(data.shape[0],*self.out_shape)
        out_var  = torch.zeros(data.shape[0],*self.out_shape)
        for i in range(data.shape[0]):
            input_data = data[i]
            X = torch.zeros((2,data.size(1)))
            X[0,:] = input_data
            X[1,:] = self.noise*torch.ones(input_data.size())
            out = self.layers(X)
            out_mean[i] = out[0,:]
            out_var[i]  = out[1,:]
        return {'mean':out_mean, 'var': out_var} 

class Dropout_Model_Builder(torch.nn.Module):

    def __init__(self, model, **kwargs):
        super(Dropout_Model_Builder, self).__init__()
        self.in_size = model.prop['input_size']
        self.out_shape = model.prop['output_shape']
        lay_names = []
        for i in range(len(model.layers)):
            lay_names.append(repr(type(model.layers[i])).split(".")[-1].split("'")[0])
        self.lay_names = lay_names
        self.in_model = model
        if 'Dropout' in lay_names:
            indx = lay_names.index('Dropout')
            p_drop = model.layers[indx].p
            drop_in = True
        else:
            p_drop = 0.05 # This the default dropout rate for the dropout masks
            drop_in = False
        layers = []
        for i in range(len(model.layers)):
            if drop_in:
                if lay_names[i] == 'Dropout':
                    layers.append(torch.nn.Dropout(p = p_drop))
                else:
                    layers.append(model.layers[i])
            else:
                if lay_names[i] in ['ReLU','ELU','Hardsigmoid','SELU','Sigmoid','Softmax','Softplus','Softsign','Tanh']:
                    layers.append(model.layers[i])
                    layers.append(torch.nn.Dropout(p = p_drop))
                else:
                    layers.append(model.layers[i])
        self.layers = torch.nn.Sequential(*layers)

    def forward(self,data):
        if self.lay_names[0] == 'Linear':
            data = data.reshape(data.shape[0],self.in_size) #This will need to be update to use size and shape function
            out = self.layers(data)
            out = out.reshape(data.shape[0],*self.out_shape)
        elif self.lay_names[0] == 'Conv2d':
            out = self.layers(data)
            out = out.reshape(data.shape[0],*self.out_shape)
        elif self.lay_names[0] == 'LSTM':
            out =  self.layers(data)
        return out

def save_results(T,N,uq_weights,uq_means,pred_mean,y_real,output,data_type=None,log_dir='logs',**kwargs):
    # data_var = (uq_weights[0]/T)*sum(uq_vars['trained'].values())+uq_weights[1]*sum(uq_vars['Unc'].values())/(T*N)
    logging.debug('-'*40)
    logging.debug('Average predicted mean  : %.5f' % numpy.average(pred_mean))
    # logging.debug('Average output variance : %.5f' % numpy.average(data_var))
    model_trained_var = torch.square(torch.tensor(uq_means['trained'][0]) - torch.tensor(pred_mean)) 
    model_Unc_var = torch.square(torch.tensor(uq_means['Unc'][0]) - torch.tensor(pred_mean)) 
    for i  in range(1,T):
        model_trained_var = model_trained_var + torch.square(torch.tensor(uq_means['trained'][i]) - torch.tensor(pred_mean))
    for j in range(1,T*N):
        model_Unc_var = model_Unc_var + torch.square(torch.tensor(uq_means['Unc'][j]) - torch.tensor(pred_mean)) 
    model_var = (uq_weights[0]/T)*numpy.asarray(model_trained_var)+ (uq_weights[1]/(N*T))*numpy.asarray(model_Unc_var)
    # total_var = data_var + model_var
    if data_type=='im':
        path = os.path.join(log_dir,'output',output)
        os.makedirs(path,exist_ok=True)
        numpy.savetxt(os.path.join(path,'mean.txt'),pred_mean,fmt='%f')
        numpy.savetxt(os.path.join(path,'var.txt'),model_var,fmt='%f')
        numpy.savetxt(os.path.join(path,'y_real.txt'),y_real.cpu().detach().numpy(),fmt='%i')
    elif data_type=='ts':
        path = os.path.join(log_dir,'output',output)
        os.makedirs(path,exist_ok=True)
        trained_means = numpy.array([uq_means['trained'][key].squeeze() for key in uq_means['trained'].keys()]).T
        uq_means = numpy.array([uq_means['Unc'][key].squeeze() for key in uq_means['Unc'].keys()]).T
        numpy.savetxt(os.path.join(path,'trained_means.txt'),trained_means,fmt='%f')
        numpy.savetxt(os.path.join(path,'uq_means.txt'),uq_means,fmt='%f')
        numpy.savetxt(os.path.join(path,'pred_mean.txt'),pred_mean.squeeze(),fmt='%f')
        # numpy.savetxt(os.path.join(path,'pred_var.txt'),total_var.squeeze(),fmt='%f')

def time_series_uq_plotter(output, data, trained_means, pred_mean, pred_var, uq_means, plot_title):
    train_data   = data['train']
    valid_data   = data['valid']
    test_data    = data['test']
    y_real_train = train_data.dataset[:][1].float().detach().numpy()[:,0,0]
    y_real_valid = valid_data.dataset[:][1].float().detach().numpy()[:,0,0]
    y_real_test  = test_data.dataset[:][1].float().detach().numpy()[:,0,0]
    y_real       = numpy.concatenate((y_real_train,y_real_valid))
    test_indx    = numpy.size(y_real)
    y_real       = numpy.concatenate((y_real, y_real_test))
    x_pred       = numpy.asarray([i for i in range(test_indx,test_indx+numpy.size(y_real_test))])
    os.makedirs('plot_data/time series',exist_ok=True)
    plt.style.use('seaborn')
    plt.figure(figsize=(6,4),dpi=200)
    plt.plot(y_real,lw=0.5,zorder=1,color='grey',label='Observed')
    #for i in range(len(uq_means)):
    for i in range(3):
        plt.plot(x_pred, uq_means[i].squeeze(),lw=0.5,zorder=2,label='Trial #%i'%(i+1))
    #plt.fill_between(x_pred,
    #                 pred_mean.squeeze()-2*numpy.sqrt(pred_var.squeeze()),
    #                 pred_mean.squeeze()+2*numpy.sqrt(pred_var.squeeze()),
    #                 alpha=0.4,color='orange',zorder=3)
    #plt.fill_between(x_pred,
    #                 pred_mean.squeeze()-numpy.sqrt(pred_var.squeeze()),
    #                 pred_mean.squeeze()+numpy.sqrt(pred_var.squeeze()),
    #                 alpha=0.5,color='yellow',zorder=4)
    #for i in range(len(trained_means)):
    #    plt.plot(x_pred, trained_means[i].squeeze(),color='black',ls='dashed',lw=0.5,zorder=5)
    #plt.plot(x_pred,pred_mean.squeeze(),color='green',lw=1,zorder=6)
    plt.xlim([2800,3200])
    plt.ylim([0,1])
    plt.xlabel('Day')
    plt.ylabel('Normalized Temperature')
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig(os.path.join('logs/output',output,'time_series',plot_title+'.pdf'))
    plt.close()
