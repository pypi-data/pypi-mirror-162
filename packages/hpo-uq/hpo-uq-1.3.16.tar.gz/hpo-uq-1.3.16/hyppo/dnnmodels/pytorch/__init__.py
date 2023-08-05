# System
import os
import logging
import time
import importlib

# External
import numpy
import torch
import matplotlib.pyplot as plt
from torch.nn.parallel import DistributedDataParallel

# Local
from .uq import uq_quantifier

class PyTorchTrainer():
    
    def __init__(self,data=None,hyperprms=None,dl_type=None,debug=False,output='out001',log_dir='logs',
                 device=torch.device('cpu'),device_ids=[],split='data',mcd=False,**kwargs):
        """
        PyTorch training method. This will train built-in models available from HYPPO.
        The built-in model of your choice can be specified using the `dl_type` variable.

        Parameters
        ----------
        data : :py:class:`dict`
          Input data sets.
        hyperprms : :py:class:`dict`
          Input set of hyperparameter values.
        dl_type : :py:class:`str`
          Type of deep learning architecture to use.
        debug : :py:class:`bool`
          Flag to estimate full training processing time.
        device : :class:`torch.device`
          Processor type to be used (CPU or GPU)
        device_ids : :py:class:`list`
          Rank of current processor used (used for data splitting)
        output : :py:class:`str`
          Output directory name to save results.
        log_dir : :py:class:`str`
          Relative path where log files are stored
        split : :py:class:`str`
          What will be split across available resources

        Returns
        -------
        The following outputs are stored and returned in the form of a dictionary:

        loss : :py:class:`float`
          Final training loss 
        models : :py:class:`str`
          Path to saved trained model
        data : :py:class:`dict`
          Input data
        criterion : :class:`torch.nn.modules.loss`
          Loss function used for training
        hyperprms : :py:class:`dict`
          Dictionary of hyperparameter values

        Examples
        --------
        """
        self.data = data
        self.device = device
        self.checkpoint_dir = os.path.join(log_dir,'checkpoints',output)
        self.state_path = os.path.join(self.checkpoint_dir,'model.pt')
        # Architecture initialization
        module = importlib.import_module('.' + dl_type.lower(), 'hyppo.dnnmodels.pytorch')
        self.model = module.get_model(data=self.data['train'], prms=hyperprms, **kwargs).to(self.device)
        self.model(torch.ones(1,*self.data['train'].dataset[0][0].shape).to(self.device))
        if not mcd:
            logging.info('-'*40)
            logging.info('Number of parameters : {:,d}'.format(sum(p.numel() for p in self.model.parameters())))
            logging.info('-'*40)
        if len(device_ids)>0 and split=='data':
            self.model(torch.ones(1,*self.data['train'].dataset[0][0].shape).to(self.device))
            self.model = DistributedDataParallel(self.model, device_ids=device_ids)
        # Check if debugging mode (summary display) requested
        if debug==1:
            from torchsummary import summary
            print(summary(self.model,self.data['train'].dataset[0][0].shape))
            quit()
        # Initialize loss function
        self.criterion = hyperprms['loss'](**hyperprms['loss_args'])
        
    def train(self,itrial=0,trial=1,accuracy=False,validate=True,rank=0,split='data',debug=False,hyperprms=None,**kwargs):
        """
        Parameters
        ----------
        itrial : :py:class:`int`
          Index of current trial.
        trial : :py:class:`int`
          Number of independent trials to run.
        accuracy : :py:class:`bool`
          Whether to calculate estimate, e.g., for classification.
        validate : :py:class:`bool`
          Use validation dataset to evaluate the model at the end of each epoch.
        rank : :py:class:`int`
          Current processor rank
        """
        # Initialize optimizer
        optimizer = hyperprms['optimizer'](self.model.parameters(),**hyperprms['opt_args'])
        # Train single trial
        t0 = time.time()
        for epoch in range(1 if debug==2 else hyperprms['epochs']):
            logging.info('-'*40)
            logging.info('{} {:>3} / {:<3} {:>14} {:>3} / {:<3}'.format('TRIAL',itrial+1,trial,'EPOCH',epoch+1,hyperprms['epochs']))
            logging.info('-'*40)
            self.model.train()
            # Perform training
            start_time = time.time()
            train_loss, train_acc = 0, 0
            logging.info('   TRAINING')
            logging.info('{:>12} : {:>11}'.format('Size',len(self.data['train'].sampler)))
            for i,(target,label) in enumerate(self.data['train']):
                target = target.float().to(self.device)
                label = label.float().to(self.device)
                if type(self.criterion).__name__=='CrossEntropyLoss':
                    label = label.long()
                optimizer.zero_grad()
                out = self.model(target)
                loss = self.criterion(out, label)
                train_loss += loss.item()
                loss.backward()
                optimizer.step()
                if accuracy:
                    n_correct = self.get_accuracy(out,label)
                    train_acc += n_correct
            train_loss /= (i+1)
            logging.info('{:>12} : {:>11.5f}'.format('Loss',train_loss))
            if accuracy:
                train_acc /= len(self.data['train'].sampler)
                logging.info('{:>12} : {:>11.5f} %'.format('Acc.',100*train_acc))
            logging.info('{:>12} : {:>11.5f} s'.format('Time',time.time()-start_time))
            self.model.eval()
            if validate:
                logging.info('   VALIDATION')
                self.model.eval()
                self.evaluate(accuracy=accuracy,**kwargs)
        # Evaluate trained model with test dataset
        logging.info('-'*40)
        logging.info('{} {:>3} / {:<3} {:>24}'.format('TRIAL',itrial+1,trial,'TESTING'))
        logging.info('-'*40)
        self.model.eval()
        self.test_loss = self.evaluate(test=True, **kwargs)
        # Save model if requested
        if split=='trial' or (split=='data' and rank==0):
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            torch.save(self.model.state_dict(),self.state_path)

    def evaluate(self, accuracy=False, test=False, update=False, mcd=False, **kwargs):
        data = self.data['test'] if test else self.data['valid']
        start_time = time.time()
        if not mcd:
            logging.info('{:>12} : {:>11}'.format('Size',len(data.sampler)))
        y_pred, acc = [], 0
        target, label = next(iter(data))
        target = target.float().to(self.device)
        label = label.float().to(self.device)
        if update and label.dim()>1 and label.shape[-1]==1:
            input_data = target[0].unsqueeze(0)
            y_real = data.dataset[:][1].float()
            for i in range(len(data.dataset)):
                out = self.model(input_data.float())
                y_pred.extend(out)
                input_data = torch.cat([input_data,out],dim=3)[:,:,:,1:]
        else:
            y_real = []
            for target,label in data:
                target = target.float().to(self.device)
                label = label.float().to(self.device)
                if type(self.criterion).__name__=='CrossEntropyLoss':
                    label = label.long()
                out = self.model(target.float())
                y_real.extend(label)
                y_pred.extend(out)
                if accuracy:
                    acc += self.get_accuracy(out,label)
            y_real = torch.tensor(y_real)
        self.y_real = y_real.to(self.device)
        self.y_pred = torch.stack(y_pred).to(self.device)
        loss = self.criterion(self.y_pred, self.y_real)
        if mcd:
            logging.debug('    trained_val : %.5f' % (loss))
            logging.debug('    trained_pred: %.5f' % (numpy.average(self.y_pred.cpu().detach().numpy())))
            logging.debug('    y_real      : %.5f' % (numpy.average(self.y_real.cpu().detach().numpy())))
        else:
            logging.info('{:>7} Loss : {:>11.5f}'.format('Test' if test else '',loss))
            if accuracy:
                logging.info('{:>7} Acc. : {:>11.5f} %'.format('Test' if test else '',100*acc/len(data.sampler)))
            logging.info('{:>12} : {:>11.5f} s'.format('Time',time.time()-start_time))
        return loss

    def get_accuracy(self,output,label):
        _, preds = torch.max(output, 1)
        n_correct = preds.eq(label).sum().item()
        return n_correct

def train(**kwargs):
    pt = PyTorchTrainer(**kwargs)
    pt.train(**kwargs)
    return pt.test_loss

def inference(**kwargs):
    pt = PyTorchTrainer(**kwargs)
    pt.model.load_state_dict(torch.load(pt.state_path))
    pt.evaluate(**kwargs)
    return pt.y_real, pt.y_pred
    
def mcd(**kwargs):
    """
    Execute Monte-Carlo Dropout Algorithm. This function loads the trained model
    architecture and does uncertainty quantification using MC dropout technique.
    """
    trainer = PyTorchTrainer(**kwargs)
    pred_mean_obj_val, pred_std = uq_quantifier(trainer, **kwargs)
    return pred_mean_obj_val, pred_std

    