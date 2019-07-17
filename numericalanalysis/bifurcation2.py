import numpy as np
from numpy import pi as π
from scipy import optimize
import math as m
import warnings
from params import params
from tqdm import tqdm
# python doesn't have a sign function builtin
sign = lambda x: m.copysign(1, x)

def type_debugs(vardict):
    for k,v in vardict.items():
        print("'{}': {}".format(k, type(v)))
        if isinstance(v, np.ndarray):
            print("\t{}".format(v.shape))

def tau_s(params, s, tau_goal):
    w0_sqr = params.w0**2
    r = params.r
    x_i = params.x_i
    phi = params.phi

    newfac = 1 - r*np.sin(phi-x_i*s + s) / np.sin(s)

    tau_at_s = s / (2*w0_sqr) * (
        newfac * np.tan(s) 
        + np.sqrt((newfac * np.tan(s))**2 + 4*w0_sqr)
    )

    return tau_at_s - tau_goal

def gamma_s(params, s):
    w0_sqr = params.w0**2
    r = params.r
    x_i = params.x_i
    phi = params.phi

    newfac = 1-r*np.cos(phi-x_i*s)
    return newfac/np.cos(s)


def gamma_n(params, tau, n):
    eps = np.finfo('double').eps

    w0 = params.w0
    ep = params.ep

    # lower possible bound on the solution
    lbound = max(
        0,
        (2*n-1)/2*π+10*eps
    )

    # upper bound for the solution
    ubound = (2*n+1)/2*π-10*eps

    # Indices of times tau[i] s.t. tau[i] >= n*π/w0
    idx_right = np.nonzero((tau - n*π/w0) >= 0)

    # and indices of times s.t. tau[i] < n*π/w0
    idx_left = np.nonzero((tau - n*π/w0) < 0)

    s = np.zeros_like(tau)

    x = n*π
    
    for i in idx_right:
        tau_goal = tau[i]

        x_0 = x-0.01

        # this snippet constrains the upper bound further
        j=0
        while (-m.tan(ubound) > 1e6 or (np.abs(tau_s(params, ubound, tau_goal)) > 1e8).all()):
            j+=1
            ubound -= 10**j*eps

        type_debugs(locals())
        signof_ubound = sign(tau_s(params, ubound, tau_goal))

        j=0
        while (signof_ubound == sign(tau_s(params, x_0, tau_goal))):
            j += 1
            x_0 = x_0 - 10**j*eps
        
        result = optimize.root_scalar(
            lambda x: tau_s(params, x, tau_goal),
            bracket=(x_0, ubound)
        )

        if not result.converged:
            raise RuntimeError("Could not converge on iteration {}".format(i))
        s[i] = result.root
    
    x = n*π
    for i in reversed(idx_left):
        tau_goal = tau[i]
        x_0 = x+0.01

        j=0
        while (abs(tau_s(params, lbound, tau_goal)) > 1e8):
            j += 1
            lbound = lbound + 10**j * eps
        
        signof_lbound = sign(tau_s(params, lbound, tau_goal))

        while (signof_lbound == sign(tau_s(params, x_0, tau_goal))):
            j += 1
            x_0 = x_0 + 10**j * eps
        
        result = optimize.root_scalar(
            lambda x: tau_s(params, x, tau_goal),
            bracket=(lbound, x_0)
        )

        if not result.converged:
            raise RuntimeError("Could not converge on iteration {}".format(i))
        s[i] = result.root

    gamma_out = gamma_s(params, s)
    Om = s / tau

    max_err = np.max(np.abs(tau_s(params, s, tau)))
    if (max_err > 1e-10):
        warnings.warn("Maximum error '{}' for tau is larger than limit of '1e-10'".format(max_err))
    
    return gamma_out, Om

if __name__ == "__main__":
    defaultparams = params()
    tau = np.linspace(0.01*defaultparams.THmax, 3.5*defaultparams.THmax, 300)
    nmax = 10
    ns = np.arange(0,nmax, 2)

    # First, curves w/o coupling:
    par = params(phi=0,r=0)
    print("Calculating uncoupled curves...")
    gc0 = np.zeros((len(ns), len(tau)))
    for n in tqdm(ns):
        g, o = gamma_n(par, tau, n)
        gc0[n,:] = g
    
    print(gc0)
