# External
import torch

# Local
from .utils import shape_and_size

class PytorchCNN(torch.nn.Module):
    """
    PyTorch class for convolutional neural network model.
    """
    def __init__(self, data=None, prms=None, **kwargs):
        """
        Initialize the model based on data properties and hyperparameter set.
        
        Parameters
        ----------
        in_shape : :py:class:`~torch.Tensor`
          Shape of input data sample to be fed to the network.
        out_shape : :py:class:`~torch.Tensor`
          Shape of output data sample that comes out of the network.
        prms : :py:class:`dict`
          Input set of hyperparameter values.
        """
        super(PytorchCNN, self).__init__()
        self.prop = shape_and_size(data, **kwargs)
        layers = []
        # CNN layers
        for ii in range(prms['layers']):
            layers.append(
                torch.nn.Conv2d(
                    in_channels  = self.prop['input_shape'][0]*prms['factor']**ii,
                    out_channels = self.prop['input_shape'][0]*prms['factor']**(ii+1),
                    kernel_size  = prms['kernel'][ii],
                    padding      = prms['padding'][ii],
                    stride       = prms['stride'][ii],
                )
            )
            layers.append(
                prms['activation'][ii]()
            )
            if prms['maxpool'][ii]!=0:
                layers.append(
                    torch.nn.MaxPool2d(
                        kernel_size = prms['maxpool'][ii],
                        stride      = None,
                    )
                )
            if prms['dropout'][ii]!=0:
                layers.append(
                    torch.nn.Dropout(
                        p = prms['dropout'][ii],
                    )
                )
        # flatten
        layers.append(
            torch.nn.Flatten()
        )
        layers.append(
            torch.nn.LazyLinear(
                out_features = prms['fc_nodes'],
            )
        )
        layers.append(
            prms['fc_activation']()
        )
        if prms['fc_dropout']!=0:
            layers.append(
                torch.nn.Dropout(
                    p = prms['fc_dropout'],
                )
            )
        # output
        layers.append(
            torch.nn.LazyLinear(
                out_features =self.prop['output_size'],
            )
        )
        self.layers = torch.nn.Sequential(*layers)
        self.layers_to_use = layers

    def forward(self,data):
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
        # out = self.layers(data)
        out = data
        for layer in self.layers_to_use:
            out = layer(out)
        out = out.reshape(data.shape[0],*self.prop['output_shape'])
        return out

def get_model(**kwargs):
    """
    Constructs the CNN model.
    """
    return PytorchCNN(**kwargs)