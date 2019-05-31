import utils, settings
import numpy as np
import matplotlib.pyplot as plt
import sys

def seriesrange(series):
    return np.max(series) - np.min(series)

def main(fname):
    data, metadata = utils.load(fname)

    freqs = np.arange(metadata['fmin'], metadata['fmax'], metadata['fstep'])

    gains = np.array([
        seriesrange(obs[1])/seriesrange(obs[0])
        for obs in data
    ])

    print(len(freqs), len(gains))

    plt.scatter(freqs, gains, marker='.')
    plt.show()

if __name__ == "__main__":
    main(settings.DATA_DIR / "delay" / sys.argv[1])