import digipot
import settings
import utils
import visa
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.stats import linregress
import sys


def main(chan, fname):
    rm = visa.ResourceManager()

    meter = None
    for res in rm.list_resources():
        if settings.METER_ID in res:
            meter = rm.open_resource(res)
    if meter is None:
        raise IOError("Could not connect to multimeter")
    meter.timeout = 10000

    inputrange = np.arange(0,256)
    outrange = np.zeros(256)


    with digipot.DigiPot() as dp:
        for i in tqdm(inputrange):
            dp.set(chan, i)
            outrange[i] = meter.query("MEAS:RES? 1E5")
    
    slope, intercept, _, _, _ = linregress(inputrange, outrange)

    plt.scatter(inputrange, outrange, marker='.')
    plt.plot(inputrange, intercept + slope * inputrange)
    plt.xlabel("Input")
    plt.ylabel("$R(\\Omega)$")
    plt.show()

    utils.save(settings.DATA_DIR / 'digipot' / fname, np.array([inputrange, outrange]), {})

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("Arguments: potentiometer #, fname")
    main(int(argv[1])-1,argv[2])