from ranpy import Ranpy
import pandas as pd
import numpy as np
from scipy.optimize import minimize, differential_evolution, NonlinearConstraint
import matplotlib.pyplot as plt
R = Ranpy(2022)




# def fit_CI(lb, ub, alpha, dist):
#     """Fit parameters for a chosen distribution with specified alpha/2 and
#     1-alpha/2 inverse cumulative distribution function values. 
    
#     Parameters
#     ----------
#     lb : scalar
#         Value of inverse cumulative distribution function at alpha/2.
#     ub : scalar
#         Value of inverse cumulative distribution function at 1-alpha/2.
#     alpha : scalar
#         Value between 0 and 1 giving the distribution mass outside of [lb, ub]. 
#     dist : str
#         Distribution being fitted. Must be one of 'beta', 'gamma', 'truncnorm', 'lognorm' or 'fixed'. 

#     Return
#     -------
#     params : dict
#         A dictionary... 
        
#     Examples
#     --------

#     """
    
lb = 0.8
ub = 1
alpha = 0.1
dist = 'fixed'

print(R.fit_CI(lb, ub, alpha, dist))