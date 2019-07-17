import settings
import utils
from scipy.stats import linregress
import matplotlib.pyplot as plt
import numpy as np


def main():
    summary = np.zeros((6,3))

    for i in range(1,7):
        dat, _ = utils.load(settings.DATA_DIR / "digipot" / "pot{}".format(i))

        slope, intercept, _, _, _ = linregress(*dat)

        frame = summary[i-1]
        frame[0] = i
        frame[1] = slope
        frame[2] = intercept

        print("Pot. {}: m={:3f}, b={:.3f}".format(i,slope,intercept))
        plt.plot(dat[0], dat[1] - (slope * dat[0] + intercept), marker='.')
        plt.title("Residuals for pot. {}".format(i))
        plt.xlabel("Input")
        plt.ylabel("Residual resistance ($\\Omega$)")
        plt.savefig(settings.FIG_DIR / 'digipot' / "pot{}_resids.pdf".format(i))
        plt.show()

        
    utils.save(settings.DATA_DIR / 'digipot' / 'potentiometers', {})


if __name__ == "__main__":
    main()