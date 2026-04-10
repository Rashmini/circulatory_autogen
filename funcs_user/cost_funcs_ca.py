import numpy as np
import casadi as ca
import os
import sys
import sympy

"""
These functions can be used as cost functions. Specify a name of one of these functions as the "cost_type" in obs_data.json to
use it as the cost.

When making your own cost function make sure it works for scalars and vectors. Otherwise put an error message so that if it is used
for the wrong data type it gets called out and stopped.
"""
def is_MLE(func):
    func.is_MLE = True
    return func

@is_MLE
def gaussian_MLE(output, desired_mean, std, weight):
    cost = ca.power((output - desired_mean)/std, 2)*weight
    if hasattr(output, '__len__'):
        # if entry is a vector then turn the vector of costs for each data point into a average cost
        cost = ca.sum(cost)/len(output)
    
    return cost

# TODO we need to create derivative functions for each cost with respect to the outputs so that we can pass 

def MSE(*args, **kwargs):
    # The mean squared error cost is the same as the 
    return gaussian_MLE(*args, **kwargs)

# TODO: Add other cost funcs
