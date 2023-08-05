import numpy

def data_split(sequence, n_timestamp, n_out, library, step=1, **kwargs):
    X, y = [], []
    for i in range(0,len(sequence),step):
        end_ix = i + n_timestamp
        if end_ix > len(sequence)-n_out:
            break
        # i to end_ix as input
        # end_ix as target output
        seq_x, seq_y = sequence[i:end_ix].T, sequence[end_ix:end_ix+n_out]
        X.append([seq_x])
        y.append([seq_y.T])
    X_data = numpy.array(X)
    y_data = numpy.array(y)
    if library=='tf':
        X_data = X_data.transpose(0,2,3,1)
        y_data = y_data.transpose(0,2,3,1)
    return {'X_data':numpy.array(X), 'y_data':numpy.array(y)}

