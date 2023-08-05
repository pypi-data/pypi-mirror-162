# Externals
import numpy
import torch
import torchsummary

# Locals
from .utils import pytorch_dict

class PytorchLSTM(torch.nn.Module):
    def __init__(self, opti, hyperprms):
        super(PytorchLSTM, self).__init__()
        layers = []
        for ii in range(hyperprms['layers']):
            if ii == 0:
                layers.append(torch.nn.LSTM(opti.X_train.shape[1],hyperprms['hidden_units'][ii]))
            else:
                layers.append(torch.nn.LSTM(hyperprms['hidden_units'][ii-1],hyperprms['hidden_units'][ii]))
            layers.append(pytorch_dict[hyperprms['activation'][ii]]())
            if hyperprms['dropout'][ii]!=0:
                layers.append(torch.nn.Dropout(p=hyperprms['dropout'][ii]))
        layers.append(torch.nn.Linear(hyperprms['hidden_units'][-1],opti.n_out))
        self.layers = torch.nn.Sequential(*layers)

    def forward(self,data):
        return self.layers(data)

def train(hyperprms, opti):

    # Single cell LSTM
    model = PytorchLSTM(opti,hyperprms)
    print(model)
    if opti.verbose>=2:
        torchsummary.summary(model, (1, opti.X_train.shape[-1]))
    quit()
    loss_function = pytorch_dict[hyperprms['loss']]()
    optimizer = torch.optim.Adam(model.parameters())

    # train
    epoch_loss = []
    for epoch in range(5):
        losses = []
        for target,label in opti.train_loader:
            model.zero_grad()
            out = model(target.float())
            loss = loss_function(out, label.float())
            losses.append(loss.data)
            loss.backward()
            optimizer.step()
        epoch_loss.append(numpy.mean(losses))
        if opti.verbose>=2:
            print("Epoch is {}, loss is {}".format(epoch+1, numpy.mean(losses)))
            plot_loss(epoch_loss)

    return model

def evaluate(model, opti):
    # test
    y_predicted = []
    for target,label in opti.test_loader:
        y_predicted.extend(model(target.float())[:,0].data)
    y_predicted = numpy.array(y_predicted).reshape(opti.y_test.shape)
    return y_predicted
