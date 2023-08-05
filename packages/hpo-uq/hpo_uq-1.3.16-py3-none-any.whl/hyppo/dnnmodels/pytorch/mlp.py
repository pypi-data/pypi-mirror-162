# External
import torch

# Local
from .utils import shape_and_size

class PytorchMLP(torch.nn.Module):
    """
    PyTorch class for multi-layer perceptron model.
    
    Examples
    --------
    Let's consider the following random hyperparameters:
    
    >>> prms = {'layers':2,'nodes':[20,20],'activation':[torch.nn.ReLU,torch.nn.ReLU],'dropout':[0.1,0.1]}
    
    Let's consider the input dataset to be the CIFAR10 dataset, we can load the PyTorch
    dataloader as follows:
    
    >>> from hyppo.datasets.cifar10 import get_data
    >>> from hyppo.datasets.loaders import get_loader
    >>> data = get_data(library='pt')
    >>> loaders = get_loader(data, batch=10)
    
    The MLP model can then be built as follows (remember, the CIFAR10 dataset requires
    the ``n_classes`` parameter to be set to 10):
    
    >>> from hyppo.dnnmodels.pytorch.mlp import PytorchMLP
    >>> PytorchMLP(data['train'],prms,n_classes=10)
    PytorchMLP(
      (layers): Sequential(
        (0): Linear(in_features=1024, out_features=20, bias=True)
        (1): ReLU()
        (2): Dropout(p=0.1, inplace=False)
        (3): Linear(in_features=20, out_features=20, bias=True)
        (4): ReLU()
        (5): Dropout(p=0.1, inplace=False)
        /
        (6): Linear(in_features=20, out_features=10, bias=True)
      )
    )
    """
    def __init__(self, data=None, prms=None, **kwargs):
        """
        Initialize the model based on data properties and hyperparameter set.
        
        Parameters
        ----------
        data : :class:`~torch.utils.data.DataLoader`
          Training data.
        prms : :class:`dict`
          Input set of hyperparameter values.
        n_classes : :class:`int`
          If not None, number of output classes from the network.
        """
        super(PytorchMLP, self).__init__()
        self.prop = shape_and_size(data, **kwargs)
        layers = []
        for ii in range(prms['layers']):
            layers.append(
                torch.nn.Linear(
                    in_features  = self.prop['input_size'] if ii==0 else prms['nodes'][ii-1],
                    out_features = prms['nodes'][ii],
                )
            )
            layers.append(
                prms['activation'][ii]()
            )
            if prms['dropout'][ii]!=0:
                layers.append(
                    torch.nn.Dropout(
                        p = prms['dropout'][ii],
                    )
                )
        layers.append(
            torch.nn.Linear(
                in_features  = prms['nodes'][-1],
                out_features = self.prop['output_size'],
            )
        )
        self.layers = torch.nn.Sequential(*layers)

    def forward(self, data):
        """
        Function that performs the forward propagation. The input data are reshaped
        into a vector form then fed to the network. The output vector is then reshaped
        according to the output format.
        
        Parameters
        ----------
        data : :py:class:`~torch.Tensor`
          Input data batch.
          
        Returns
        -------
        out : :py:class:`~torch.Tensor`
          Output data out of the neural network.
        """
        data = data.reshape(data.shape[0],self.prop['input_size'])
        out = self.layers(data)
        out = out.reshape(data.shape[0],*self.prop['output_shape'])
        return out

def get_model(**kwargs):
    """
    Constructs the MLP model.
    """
    return PytorchMLP(**kwargs)
