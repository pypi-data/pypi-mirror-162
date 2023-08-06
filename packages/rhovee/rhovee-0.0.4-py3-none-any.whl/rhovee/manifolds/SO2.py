import numpy as np

def Exp(theta):
    cosine = np.cos(theta)
    sine = np.sin(theta)
    so2_mat = np.array([[cosine, -sine],[sine, cosine]])
    return so2_mat

def Log(so2_mat):
    cosine = so2_mat[0,0]
    sine = so2_mat[1,0]
    theta = np.arctan2(sine,cosine)
    return theta

def adjoint(so2_mat):
    return 1.0

