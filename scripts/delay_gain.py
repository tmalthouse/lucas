import utils, settings
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.stats import linregress

def seriesrange(series):
    return np.max(series) - np.min(series)

def main(fname):
    data, metadata = utils.load(fname)

    freqs = np.arange(metadata['fmin'], metadata['fmax'], metadata['fstep'])

    gains = np.array([
        seriesrange(obs[0])/seriesrange(obs[1])
        for obs in data
    ])

    gain_slope, gain_intercept, _, pval, _ = linregress(freqs, gains)


    plt.scatter(freqs, gains, marker='.')
    plt.plot(freqs, gain_intercept + freqs*gain_slope, label="$G=({:.2E})f + {:.2f}$\n$P$[$G=$const]$={:.4f}$".format(gain_slope, gain_intercept, pval))
    plt.legend()
    plt.xlabel("$f$(Hz)")
    plt.ylabel("$G$")
    plt.show()

if __name__ == "__main__":
    main(settings.DATA_DIR / "delay" / sys.argv[1])