import utils, settings
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.stats import linregress
import scipy.interpolate as interpolate
import scipy.optimize as opt
import math as m

def seriesrange(series):
    return np.max(series) - np.min(series)

def find_params(freqs, gains):
    spline = interpolate.UnivariateSpline(freqs, gains, s=0.01)

    A0 = np.max(gains)
    # Often, we have two points w/ max gain (due to discrete values off the scope)
    f0 = np.mean(freqs[np.where(gains == A0)])

    dB3_gain = (1/m.sqrt(2))*A0

    def spline_shifted(f):
        return spline(f) - dB3_gain
    

    dB1 = opt.root_scalar(spline_shifted, bracket=(freqs[0], f0)).root
    dB2 = opt.root_scalar(spline_shifted, bracket=(f0, freqs[-1])).root

    df = dB2 - dB1

    print(A0,f0,dB3_gain, df)
    return {
        'A0': A0,
        'f0': f0,
        'df': df,
        'Q': f0/df,
        'fn': spline,
        '3dBGain': dB3_gain
    }

def main(fname):
    data, metadata = utils.load(fname)

    warning_printed = False
    for series in data:
        if np.min(series) == -128:
            if not warning_printed:
                print("Warning: missing data in series. Interpreting as 0. This occurs with very low refresh rates.".format(series))
                warning_printed = True
            series[series == -128] = 0

    freqs = np.arange(metadata['fmin'], metadata['fmax'], metadata['fstep'])

    gains = np.array([
        seriesrange(obs[0])/seriesrange(obs[1])
        for obs in data
    ])

    params = find_params(freqs,gains)



    plt.scatter(freqs, gains, marker='.')
    plt.plot(freqs, params['fn'](freqs), label="$A_0 = {A0:.2f}$\n$f_0 = {f0:.2f}$Hz\n$Q={Q:.2f}$".format(**params))

    plt.axhline(params['3dBGain'], color='red', linestyle='dashed', label="3dB point")
    plt.legend()
    plt.xlabel("$f$(Hz)")
    plt.ylabel("$G$")

    plt.savefig(settings.FIG_DIR / "filters" / "{}.pdf".format(fname.stem))
    plt.show()

if __name__ == "__main__":
    main(settings.DATA_DIR / "filters" / sys.argv[1])

