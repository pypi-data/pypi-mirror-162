# Externals
import numpy
import tensorflow as tf
tf_version= tf.__version__[0]
if tf_version == str(1):
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Flatten, Reshape
    from keras.layers.convolutional import Conv1D, MaxPooling1D
    from keras.layers.recurrent import SimpleRNN, LSTM, GRU
    from tensorflow import set_random_seed
elif tf_version == str(2):
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, Flatten, Reshape
    from tensorflow.keras.layers import Conv1D, MaxPooling1D
    from tensorflow.keras.layers import SimpleRNN, LSTM, GRU

# Locals
from ..plots import plot_loss
    
def train(data, hyperprms, **kwargs):
    # Extract input and output data size
    in_shape  = data['train']['X_data'].shape[1:]
    in_size   = numpy.prod(in_shape)
    out_shape = data['train']['y_data'].shape[1:]
    out_size  = numpy.prod(out_shape)
    # Build model
    model = Sequential()
    #model.add(Reshape((in_size,), input_shape=in_shape))
    for ii in range(hyperprms['layers']):
            if ii == 0:
                if hyperprms['layers'] == 1:
                    model.add(LSTM(hyperprms['hidden_units'][ii], 
                                    activation=hyperprms['activation'][ii],
                                    recurrent_dropout=hyperprms['recurrent_dropout'][ii],
                                    return_sequences=False,
                                    input_shape=(in_size,1)))#(param['lag']+1, n_features)))
                else:    
                    model.add(LSTM(hyperprms['hidden_units'][ii], 
                                    activation=hyperprms['activation'][ii],
                                    recurrent_dropout=hyperprms['recurrent_dropout'][ii],
                                    return_sequences=True,
                                    input_shape=(in_size,1)))
    
            else:
                if ii < hyperprms['layers']-1:
                    model.add(LSTM(hyperprms['hidden_units'][ii], 
                                    return_sequences=True,
                                    activation=hyperprms['activation'][ii],
                                    recurrent_dropout=hyperprms['recurrent_dropout'][ii]))
                else:          
                    model.add(LSTM(hyperprms['hidden_units'][ii], 
                                    activation=hyperprms['activation'][ii],
                                    recurrent_dropout=hyperprms['recurrent_dropout'][ii]))
            if hyperprms['dropout'][ii]!=0:
                model.add(Dropout(hyperprms['dropout'][ii]))
    # output
    model.add(Dense(units=out_size))
    #model.add(keras.layers.Reshape(out_shape, input_shape=(out_size,)))
    # train
    model.compile(loss=hyperprms['loss'], optimizer=hyperprms['optimizer'])

    # Reshape into [#samples, timestamps, features]
    #opti.X_train = opti.X_train.reshape(opti.X_train.shape[0],
    #                                    opti.X_train.shape[1])
    #opti.X_test = opti.X_test.reshape(opti.X_test.shape[0],
    #                                  opti.X_test.shape[1])
    
    history = model.fit(data['train']['X_data'], data['train']['y_data'],
                        verbose=1,
                        batch_size=hyperprms['batch'], 
                        epochs=hyperprms['epochs'],
                        shuffle=False)
    
    if opti.verbose>=2:
        plot_loss(history.history['loss'])
    
    return model

def evaluate(model, opti):
    if opti.update:
        y_predicted = opti.X_test[0].flatten()
        for i in range(len(opti.X_test)):
            data = y_predicted[i:i+opti.X_test.shape[1]].reshape(1,*opti.X_test.shape[1:])
            out = model.predict(data)
            y_predicted = numpy.concatenate((y_predicted,out.flatten()))
        y_predicted = y_predicted[opti.X_test.shape[1]:].reshape(-1,1)
    else:
        y_predicted = model.predict(opti.X_test)
    return y_predicted
