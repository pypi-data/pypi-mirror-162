__version__ = '0.1.6a3'

import numpy as np

def matmul(a,b):
    assert a.shape == b.shape
    assert a.shape[0] == a.shape[1]
    sides = a.shape[0]
    c = np.zeros(a.shape)
    for i in range(sides):
        for j in range(sides):
            for k in range(sides):
                c[i][j] += a[i][k] * b[k][j]
    return c
