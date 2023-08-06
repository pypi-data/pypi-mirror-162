import numpy as np
from . import SO2
from .utils import *



def to_Rt(SE2_mat):
    rot_mat = SE2_mat[:2,:2]
    t = SE2_mat[:2,2]
    return rot_mat, t


def V_helper(theta):
    if np.isclose(theta, 0):
        return np.identity(2)
    V = np.sin(theta)/theta * np.identity(2) + (1-np.cos(theta))/theta*skew2(1)
    return V

def V_inv_helper(theta):
    return np.linalg.inv(V_helper(theta))

def Exp(vec):
    assert vec.shape == (3,)
    SE2_mat = np.identity(3)
    theta = vec[2]
    rho = vec[:2]
    SO2_mat = SO2.Exp(theta)
    SE2_mat[:2,:2] = SO2_mat
    t = V_helper(theta)@rho
    SE2_mat[:2, 2] = t
    return SE2_mat

def Log(SE2_mat):
    assert SE2_mat.shape == (3,3)
    vec = np.zeros(3)
    R,t = to_Rt(SE2_mat)
    theta = SO2.Log(R)
    rho = V_inv_helper(theta)@t
    vec[:2] = rho
    vec[2] = theta
    return vec

def adjoint(SE2_mat):
    ad = np.identity(3)
    R,t = to_Rt(SE2_mat)
    ad[:2,:2] = R
    ad[:2, 2] = -skew2(1)@t
    return ad

def right_jacobian(vec):
    assert vec.shape == (3,)
    rho_1 = vec[0]
    rho_2 = vec[1]
    theta = vec[2]
    if np.allclose(theta, np.zeros(3)):
        return np.identity(3)
    right_jacob = np.zeros((3,3))
    sin_th = np.sin(theta)
    cos_th = np.cos(theta)
    right_jacob[0,0] = sin_th/theta
    right_jacob[1,0] = (cos_th - 1)/theta
    right_jacob[2,0] = 0.0
    right_jacob[0,1] = (1-cos_th)/theta
    right_jacob[1,1] = sin_th/theta
    right_jacob[2,1] = 0.0
    right_jacob[0,2] = (theta*rho_1 - rho_2 + rho_2*cos_th - rho_1*sin_th)/(theta**2)
    right_jacob[1,2] = (rho_1+theta*rho_2-rho_1*cos_th-rho_2*np.sin(theta))/theta**2
    right_jacob[2,2] = 1.0
    return right_jacob

def inv_right_jacobian(vec):
    assert vec.shape == (3,)
    return np.linalg.inv(right_jacobian(vec))

def left_jacobian(vec):
    assert vec.shape == (3,)
    return right_jacobian(-vec)


