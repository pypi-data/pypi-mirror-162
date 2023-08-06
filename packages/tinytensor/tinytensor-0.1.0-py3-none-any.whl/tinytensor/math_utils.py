'''
    TBH I think these shouldn't be implement here
    maybe I can offload some of these to onnxruntime?
'''
import numpy as np


def sigmoid(x):
    ex = np.exp(x)
    y = ex/(1+ex)
    return y


def softmax(x):
    '''
        Apply softmax to last dimension
    '''
    s = np.max(x, axis=-1)[:, np.newaxis]
    ex = np.exp(x - s)
    return ex/ex.sum(axis=-1)[:, np.newaxis]

