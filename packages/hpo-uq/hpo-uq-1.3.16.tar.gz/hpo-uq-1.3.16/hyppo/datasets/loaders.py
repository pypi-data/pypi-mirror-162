import numpy
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.distributed import DistributedSampler

class make_dataset(Dataset):
    def __init__(self, X_data, y_data):
        self.X_data = X_data#.reshape(X_data.shape[0],numpy.prod(X_data.shape[1:]))
        self.y_data = y_data
        self.dataset, self.labels = self.preprocess()

    def preprocess(self):
        X_data = self.X_data
        y_data = self.y_data
        final, labels = [], []
        for i in range(len(X_data)):
            final.append(numpy.array(X_data[i]))
            labels.append(numpy.array(y_data[i]))
        return torch.from_numpy(numpy.array(final)), torch.from_numpy(numpy.array(labels))
    
    def __getitem__(self,index):
        return self.dataset[index], self.labels[index]
  
    def __len__(self):
        return len(self.dataset)

def get_loader(data,batch,backend=None,split='data',model=None,shuffle=True,**kwargs):
    loaders = {}
    if model==None:
        for set_name in ['train','valid','test']:
            dataset = data[set_name]
            dataset = make_dataset(**dataset) if type(dataset).__name__=='dict' else dataset
            sampler = None if backend==None or split=='trial' else DistributedSampler(dataset)
            shuffle = shuffle if set_name=='train' else False
            loaders[set_name] = DataLoader(dataset, batch_size=batch, sampler=sampler, shuffle=shuffle)
    else:
        pred = model(torch.tensor(data['train'][0]).float())
        pred = numpy.concatenate((data['train'][0][0],
                                  pred.flatten().detach().numpy()))
        pred = numpy.array([pred[i:i+24] for i in range(len(X_train))])
        loaders['train'] = DataLoader(make_dataset(pred, y_train),
                                      batch_size=batch,
                                      shuffle=shuffle)
    return loaders
