import numpy as np
from numpy import pi as π
from scipy import optimize
import math as m
from colorama import Fore, Style
import params
from tqdm import tqdm
import inspect
import matplotlib.pyplot as plt
import IPython
import sys
from time import sleep
# python doesn't have a sign function builtin
sign = lambda x: m.copysign(1, x)


# https://stackoverflow.com/a/30408825/11760903
# The ``shoelace algorithm'' for calculating the area of an arbitrary polygon,
# given its vertices in cartesian space
# We can get the list of vertices of the polygon between two lines from Matplotlib (see below)
# and use this thing to get the associated area
# Not pretty, but dead fast.
def poly_area(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

# A little toy to help debug type errors (especially arrays where you expect scalars, and v.v.)
# Call with type_debugs(locals()), and it'll print a list of all local vars, their type, and
# (for numpy arrays) their shape
def type_debugs(vardict):
    caller = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    print("Local variables in {}:".format(caller))
    for k,v in vardict.items():
        print("'{}': {}".format(k, type(v)))
        if isinstance(v, np.ndarray):
            print("\t{}".format(v.shape))
    print('\n')

def summarize(array):
    print(f"Shape: {np.shape(array)}\nMean = {np.mean(array)}\tVar. = {np.var(array)}\nMin = {np.min(array)}\tMax = {np.max(array)}")

def τ_s(params, s, τ_goal):
    w0_sqr = params.w0**2
    r = params.r
    ξ = params.ξ
    φ = params.φ

    newfac = 1 - r*np.sin(φ-ξ*s + s) / np.sin(s)

    τ_at_s = s / (2*w0_sqr) * (
        newfac * np.tan(s) 
        + np.sqrt((newfac * np.tan(s))**2 + 4*w0_sqr)
    )


    return τ_at_s - τ_goal

def gamma_s(params, s):
    w0_sqr = params.w0**2
    r = params.r
    ξ = params.ξ
    φ = params.φ

    newfac = 1-r*np.cos(φ-ξ*s)
    return newfac/np.cos(s)


def gamma_n(params, τ, n):
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

    # print(f"LBound = {lbound}, UBound = {ubound}")

    # Indices of times τ[i] s.t. τ[i] >= n*π/w0
    # We need the [0], since .nonzero returns a tuple of nonzero elements, one per dimension
    # This is a 1d array, so the tuple only has one element
    idx_right = np.nonzero((τ - n*π/w0) >= 0)[0]


    # and indices of times s.t. τ[i] < n*π/w0
    idx_left = np.nonzero((τ - n*π/w0) < 0)[0]

    s = np.zeros_like(τ)

    x = n*π

    
    
    for i in idx_right:
        τ_goal = τ[i]

        x_0 = x-0.05

        # this snippet constrains the upper bound further
        j=0
        while (-m.tan(ubound) > 1e6 or (np.abs(τ_s(params, ubound, τ_goal)) > 1e8)):
            j+=1
            ubound -= 10**j*eps

        signof_ubound = sign(τ_s(params, ubound, τ_goal))

        j=0
        while (signof_ubound == sign(τ_s(params, x_0, τ_goal))):
            j += 1
            x_0 = x_0 - 10**j*eps
        
        result = optimize.root_scalar(
            lambda x: τ_s(params, x, τ_goal),
            bracket=(x_0 + eps, ubound - eps),
            method='brentq',
            xtol=1e-20
        )

        

        if not result.converged:
            raise RuntimeError("Could not converge on iteration {}".format(i))
        s[i] = result.root

        catch_bad_fit(τ, τ_goal, x_0, ubound, params, s, i, result, n)

        
    
    x = n*π
    for i in reversed(idx_left):
        τ_goal = τ[i]
        x_0 = x+0.05

        

        j=0
        while (abs(τ_s(params, lbound, τ_goal)) > 1e8):
            j += 1
            lbound = lbound + 10**j * eps
        
        signof_lbound = sign(τ_s(params, lbound, τ_goal))

        while (signof_lbound == sign(τ_s(params, x_0, τ_goal))):
            j += 1
            x_0 = x_0 + 10**j * eps
        
        result = optimize.root_scalar(
            lambda x: τ_s(params, x, τ_goal),
            bracket=(lbound + eps, x_0 - eps),
            method='brentq',
            xtol=1e-20
        )

        if not result.converged:
            raise RuntimeError("Could not converge on iteration {}".format(i))
        s[i] = result.root

        catch_bad_fit(τ, τ_goal, lbound, x_0, params, s, i, result, n)

        
        
        

    summarize(s)

    gamma_out = gamma_s(params, s)
    Om = s / τ
    

    max_err = np.max(np.abs(τ_s(params, s, τ)))
    if (max_err > 1e-10):
        error_mag_warning(max_err)
    # type_debugs(locals())
    # exit()
    
    return gamma_out, Om

def catch_bad_fit(τ, τ_goal, lbound, ubound, params, s, i, result, n):
    if False:#(0.78 < τ_goal < 0.88):
            rng = np.linspace(τ[0], τ[-1]*10, 1000)
            plt.close('all')
            plt.plot(rng, τ_s(params, rng, τ_goal))
            plt.plot([s[i]],0,label="Found zero point",color='red',marker='x')
            print(f"s[i]={s[i]}\tτ={τ_goal}\nopt_res = {result}\ni={i}\tn={n}\tφ={params.φ}\n")
            plt.vlines([lbound, ubound], -2,2, label="Bounding for fit")
            plt.ylim((-2,2))
            plt.xlim((0,2*s[i]))
            plt.legend()
            plt.show()

def error_mag_warning(max_err):
    tqdm.write(
        "{}WARNING:{} Maximum error '{:.3e}' for τ is larger than limit of '1e-10' ({})".format(
            Fore.YELLOW,
            Style.RESET_ALL,
            max_err,
            error_mag_warning.count
        )
    )
    error_mag_warning.count += 1
error_mag_warning.count = 0

def make_curve(ns, φ, τ, params_fn=params.default, r=None):
    if r is not None:
        par = params_fn(φ=φ,r=r)
    else:
        par = params_fn(φ=φ)
    gc0 = np.zeros((len(ns), len(τ)))
    for n in ns:
        g, o = gamma_n(par, τ, n)
        gc0[n//2,:] = g
    
    gc0[gc0 < 0] = np.inf

    crv0 = np.amin(gc0, axis=0)
    return crv0




def AD_area(τ, par, crv0, crv3, crv4, crv34, show=False, saveloc=None):
    xs = τ/par.THmax

    plt.close()
    plt.plot(xs, crv0.T, label="Uncoupled curve")
    # plt.plot(xs, crv3.T, label="Coupled curve 1")
    # plt.plot(xs, crv4.T, label="Coupled curve 2")
    # plt.plot(xs, crv34, label="Coupled curve")
    # ad_regions = plt.fill_between(xs, crv0, crv34, where=(crv34>crv0), facecolor="lightgrey", edgecolor='darkgrey', hatch='xxxx', interpolate=True)
    plt.xlabel(r"$\tau_{sf}/T_0$")
    plt.ylabel(r"$\gamma_{sf}$")
    plt.legend()

    if saveloc is not None:
        plt.savefig("{}.pdf".format(saveloc))
    if show:
        plt.show()

    poly_paths = ad_regions.get_paths()
    
    # if there are no regions of AD found
    if(len(poly_paths) == 0):
        return -10


    area = max([
        poly_area(*(p.cleaned()._vertices.T))
        for p in poly_paths
    ])
    return area




def area_from_ξ(ξ, show=False, saveloc=None, params=params.default):
    print("Iteration {}, ξ = {}".format(area_from_ξ.iter, ξ))
    area_from_ξ.iter += 1
    def params_fn(**kwargs):
        return params(ξ = ξ, **kwargs)

    defaultparams = params()
    τ = np.linspace(0.01*defaultparams.THmax, 3.5*defaultparams.THmax, 1000)
    nmax = 10
    ns = np.arange(0,nmax, 2)

    crv0 = make_curve(ns, φ=0, τ=τ, r=0, params_fn=params_fn)
    crv3 = make_curve(ns, φ=-π/2, τ=τ, params_fn=params_fn)
    crv4 = make_curve(ns, φ=π/2, τ=τ, params_fn=params_fn)

    crv34 = np.minimum(crv3, crv4)

    area = AD_area(τ, defaultparams, crv0, crv3, crv4, crv34, show=show, saveloc=saveloc)
    return area
area_from_ξ.iter = 0


def main():
    # area = area_from_ξ(1e-4)

    # opt_res = optimize.minimize_scalar(lambda ξ: -area_from_ξ(ξ), bounds=(0,1e-4), method='bounded')

    # print("Converged. Showing plot...")
    ar = area_from_ξ(5e-4, True)
    print(ar)


def main_interactive():
    ξ = 1e-4
    opt = params.default().__dict__
    p = lambda **kwargs: params.default(patch=opt, **kwargs)
    def update():
        area_from_ξ(ξ, show=True,params=p)
        plt.clear('all')
    print(
"""Launching interactive iPython console
\tTo change a parameter, set opt.<param> = <newval>
\tTo change ξ, do ξ = <newval>
\tTo update the graph, call update()
\tTo exit, call exit()"""
    )
    IPython.embed()



if __name__ == "__main__":
    main()
    

