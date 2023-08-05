from sklearn.metrics import mean_squared_error

def prediction_with_update(model, lag, test_X_in,test_Y,nn_type):
    pred_Y = []
    for num in range(test_Y.shape[0]):
        if 'mlp' == nn_type.lower():
            tmp = model.predict(np.reshape(test_X_in[num], (1,test_X_in[num].shape[0]*test_X_in[num].shape[1])), verbose=0)
        else:
            tmp = model.predict(np.reshape(test_X_in[num], (1,test_X_in[num].shape[0],test_X_in[num].shape[1])), verbose=0)
        pred_Y.append(tmp[0])
        for i in range(1,(lag+1)+1):
            if num + i < test_X_in.shape[0]: # max num = test_X.values.shape[0]-1
                    test_X_in[num+i][i-1][0] = tmp
    loss = mean_squared_error(test_Y.values, pred_Y)
    return (loss, pred_Y)
