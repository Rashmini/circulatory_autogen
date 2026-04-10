import casadi as ca

def series_to_constant(func):
    func.series_to_constant = True
    return func
    
@series_to_constant
def max(x, series_output=False):
    if series_output:
        return x
    else:
        return ca.mmax(x)

@series_to_constant
def min(x, series_output=False):
    if series_output:
        return x
    else:
        return ca.mmin(x)

@series_to_constant
def mean(x, series_output=False):
    if series_output:
        return x
    else:
        return ca.mmean(x)

@series_to_constant
def max_minus_min(x, series_output=False):
    if series_output:
        return x
    else:
        return ca.max(x) - ca.min(x)

def addition(x1, x2):
    return x1 + x2

def subtraction(x1, x2):
    return x1 - x2

def multiplication(x1, x2):
    return x1 * x2

def division(x1, x2):
    return x1 / x2

# TODO: Add other operation funcs
