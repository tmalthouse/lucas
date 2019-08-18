import math
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from tqdm import tqdm
from statistics import mode
π = math.pi

# A little toy to help debug type errors (especially arrays where you expect scalars, and v.v.)
# Call with type_debugs(locals()), and it'll print a list of all local vars, their type, and
# (for numpy arrays) their shape
def type_debugs(vardict):
    import inspect
    caller = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    print("Local variables in {}:".format(caller))
    for k,v in vardict.items():
        print("'{}': {}".format(k, type(v)))
        if isinstance(v, np.ndarray):
            print("\t{}".format(v.shape))
    print('\n')

def quadratic_from_points(pt1, pt2, pt3):
    y = np.array([pt1[1], pt2[1], pt3[1]])

    arr = np.array([
        [pt1[0]**2, pt1[0], 1],
        [pt2[0]**2, pt2[0], 1],
        [pt3[0]**2, pt3[0], 1]
    ])

    result = np.linalg.solve(arr, y)

    return lambda x: np.sum(np.linalg.solve(arr, y) * np.array([x**2, x, 1]))

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]

def vote_on_solution(idx1, idx2, idx3):
    if idx2 is not None and idx3 is not None:
        return mode([idx1,idx2,idx3])
    else:
        # If we're near the beginning of the series, the first heuristic is most likely to work
        return idx1

def polynomial_appx(Xs, Ys):
    y = Ys
    degree = len(Xs)
    print('deg=',degree)
    arr = np.zeros((degree,degree))

    for i in range(degree):
        for j in range(degree):
            arr[i,j] = pow(Xs[i], degree-j-1)
    print(arr)
    result = np.linalg.solve(arr, y)
    print(result)

    def outpoly(x):
        return np.sum(result * np.array([np.power(x, degree-j-1) for j in range(degree)]))
    return outpoly


def coupled_characteristic_eqn(omega, params):
    tau_sf = params['tau_sf']
    tau_c = params['tau_c']
    gamma_c = params['gamma_c']
    eps = ((2*π)/params['T0'])**2

    return (-(omega**2 * np.cos(omega*tau_sf)) - 
            omega * (1-gamma_c*np.sin(omega*tau_c))*np.sin(omega * tau_sf) +
            eps - 
            gamma_c * omega * np.cos(omega * tau_c) * np.cos(omega * tau_sf))

def find_roots(fn, start, stop, eps):
    x_bins = np.arange(start, stop, eps)
    y_bins = fn(x_bins)

    indices_of_interest = np.asarray(y_bins[:-1] * y_bins[1:] < 0).nonzero()[0]

    roots = np.zeros_like(indices_of_interest, dtype='double')

    for i in range(len(indices_of_interest)):
        idx = indices_of_interest[i]
        bracket = [x_bins[idx], x_bins[idx+1]]

        result = opt.root_scalar(fn, method='brentq', bracket = bracket)

        if not result.converged:
            raise RuntimeError("Root not converged!")
        roots[i] = result.root
    
    return roots




def find_gammas(taus, show=False):
    if show:
        fig = plt.figure()
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)

    par = {
        'tau_sf': 12.435,
        'tau_c': 0.124,
        'gamma_c': 0.25,
        'T0': 11.47
    }

    W = []

    for tau in tqdm(taus):
        params = par.copy()
        params['tau_sf'] = tau

        results = params.copy()


        # We find all the roots in an interval by searching a grid. For this to work, and to have reasonable
        # performance, we need to appropriately pick grid size and spacing. 
        #
        # Rationale: Oscillations scale like Omega*tau_sf and Omega should be centered at Omega=2*pi/T0
        # If we want m periods of oscillation, then DeltaOmega = m * 2*pi/tau_sf
        # should be a good choice.
        m = 4
        omega_mid = 2 * π / params['T0']

        if params['tau_sf'] == 0:
            delta_omega = 8 * π/params['T0'] * 5
        else:
            delta_omega = m*2*π/params['tau_sf'] * 5
        
        omega_low = max(0, omega_mid - delta_omega)
        omega_high = omega_mid + delta_omega
        searchbrackets = 1000
        d_omega = (omega_high - omega_low)/searchbrackets

        omegas = np.linspace(omega_low, omega_high, searchbrackets)

        if show:
            ax1.clear()
            ax1.grid()
            ax1.set_xlim(omega_low, omega_high)

        # We then have two solutions---one with a positive coupling constant, and one with negative:
        params['gamma_c'] = -1 * results['gamma_c']
        fn = lambda x: coupled_characteristic_eqn(x, params)
        omneg = find_roots(fn, omega_low, omega_high, d_omega)
        gamma_sf_neg = (1-params['gamma_c']*np.sin(omneg * params['tau_c']))/np.cos(omneg * params['tau_sf'])

        if show:
            ax1.plot(omegas, fn(omegas), color='blue', label="Negative Coupling")
            ax1.scatter(omneg, fn(omneg), color='blue', marker='x')
        


        params['gamma_c'] = results['gamma_c']
        fn = lambda x: coupled_characteristic_eqn(x, params)
        ompos = find_roots(fn, omega_low, omega_high, d_omega)
        gamma_sf_pos = (1-params['gamma_c']*np.sin(ompos * params['tau_c']))/np.cos(ompos * params['tau_sf'])

        if show:
            ax1.plot(omegas, fn(omegas), color='red', label="Positive Coupling")
            ax1.scatter(ompos, fn(ompos), color='red', marker='x')

        
        results['omega'] = np.concatenate((omneg, ompos))
        results['gamma_sf'] = np.concatenate((gamma_sf_neg, gamma_sf_pos))
        W.append(results)
    
    ax1.legend()

    out_x = []
    out_y = []
    for i in range(len(taus)):
        for res in W[i]['gamma_sf']:
            out_x.append(taus[i])
            out_y.append(res)
    
    ax2.scatter(out_x, out_y, marker='.')
    plt.show()

    g = np.zeros_like(taus)
    for i,t in enumerate(taus):
        gammas = W[i]['gamma_sf']
        pos_gammas = gammas[gammas>0]
        g[i] = np.min(pos_gammas)
    
    plt.plot(taus, g)
    plt.show()

    # We've got a bunch of points on curves, now we need to group them into curves
    # How do we do this? 
    #    In general, gamma is decreasing with increasing tau, but this is not always
    #    true
    # Algorithm idea: 
    # Given a point on the curve at step tau[i], find the largest point at tau[i+1]
    # s.t. gamma[i+1] < tau[i]
    # If this leads to a large jump in the associated omega, loosen the restriction that 
    # gamma[i+1] < tau[i]

    # Xs = taus[1:10]
    # gammas = [max(res['gamma_sf']) for res in W[1:10]]
    # appx = polynomial_appx(Xs[-4:-1], gammas[-4:-1])
    # r = np.linspace(Xs[0], Xs[-1], 1000)
    # plt.scatter(Xs, gammas)
    # plt.plot(r, np.vectorize(appx)(r))
    # plt.show()


    # We have three heuristics to determine which point is the next on the line:
    # 1) We expect omega to be decreasing, so pick the gamma corresponding to the largest
    #    decreased omega. Omega is not strictly decreasing, however, so this is not always
    #    reliable.
    # 2) Pick the point closest to the linear continuation of the  previous two points.
    #    Obviously only works for the third (and beyond) points.
    # 3) Same as #2, but use the quadratic continuation.
    # curves = []
    # for i, tau in enumerate(taus):
    #     pos_gamma_idx = W[i]['gamma_sf'] > 0
    #     W[i]['posgamma'] = W[i]['gamma_sf'][pos_gamma_idx]
    #     W[i]['posomega'] = W[i]['omega'][pos_gamma_idx]
    #     # As we assign points to lines, we want to mark them unavailable to other lines.
    #     W[i]['available'] = np.ones_like(W[i]['posgamma'], dtype=bool)

    #     # For each gamma here that hasn't already been included in a curve:
    #     for j, gamma in enumerate(W[i]['posgamma']):
    #         # Create a new curve
    #         crv = [np.array([tau,gamma])]

    #         # First heuristic: closest strictly decreasing point:

    
def follow_curve(taus, W, i, gamma, omega, curve=[]):
    initial_tau = taus[i]
    initial_gamma = gamma
    initial_omega = omega

    # If we are at tau_max, there's no more points to add
    if i == len(taus):
        return curve

    candidate_gammas = W[i+1]['posgamma']
    candidate_omegas = W[i+1]['posomega']
    availability = W[i+1]['available'] 

    # We want to set all omegas that have already been claimed as unavailable
    avl_omegas = np.where(
        # all values that have already been claimed 
        availability,
        candidate_omegas,
        # have been replaced by negative infinity
        -100000
    )

    avl_gammas = np.where(
            availability,
            candidate_gammas,
            -np.inf
    )

    # Heuristic 1: Closest decreasing omega
    # Return the index of the largest value
    candidate1_idx = np.argmax(
        # In an array where
        np.where(
            # all values greater than omega_initial
            candidate_omegas < initial_omega,
            avl_omegas,
            # have been replaced by negative infinity
            -100000
        )
    )
    candidate1_gamma = candidate_gammas[candidate1_idx]
    candidate1_omega = candidate_omegas[candidate1_idx]
    err1 = abs(initial_gamma - candidate1_gamma)

    
    # Heuristic 2: Linear continuation
    # This relies on having at least one lag available:
    if len(curve) > 0:
        # Get the coordinates of the previous point on the curve 
        lag1_tau = curve[-1][0]
        lag1_gamma = curve[-1,1]
        # create a line passing through the previous and current points
        linappx = polynomial_appx([lag1_tau, initial_tau], [lag1_gamma, initial_gamma])
        # And evaluate that line at the next tau
        est2_gamma = linappx(taus[i+1])

        candidate2_idx, candidate2_gamma = find_nearest(avl_gammas, est2_gamma)
        err2 = abs(candidate2_gamma-est2_gamma)
    else:
        candidate2_idx, candidate2_gamma = None, None
    
    # Heuristic 3: Quadratic continuation
    # This relies on having at least two lags available
    if len(curve)>1:
        lag1_tau = curve[-1][0]
        lag2_tau = curve[-2][0]
        lag1_gamma = curve[-1][1]
        lag2_gamma = curve[-2][1]

        quadappx = polynomial_appx([lag2_tau, lag1_tau, initial_tau], [lag2_gamma, lag1_gamma, initial_gamma])
        est3_gamma = quadappx(taus[i+1])

        candidate3_dix, candidate3_gamma = find_nearest(W[i+1]['posgamma'], est2_gamma)
        err3 = abs(candidate3_gamma-est3_gamma)
    
    # Democracy is the worst form of decision-making, except for all the others
    # This function, if two of the indices agree, returns that index.
    # If a lagged solution is missing, it goes with candidate1 (since the lagged
    # ones tend to be most unreliable at the beginning anyways)
    consensus = vote_on_solution(candidate1_idx, candidate2_idx, candidate3_idx)

    


    
if __name__ == "__main__":
    find_gammas(np.linspace(0,5,200), True)
