import digipot
import settings
import utils
import visa
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.stats import linregress
import sys
from time import sleep


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
            done = False
            while not done:
                try:
                    dp.set(chan, i)
                    done = True
                except OSError as err:
                    print("Caught error from controller!")
                    opt = input("(a)bort, (r)etry, (i)gnore? ")
                    if 'i' in opt:
                        done = True
                        break
                    if 'r' in opt:
                        continue
                    else:
                        raise err
                sleep(0.05)
                outrange[i] = meter.query("MEAS:RES? 1E5")
    
    slope, intercept, _, _, _ = linregress(inputrange, outrange)
    response_equation = "R = {:.1f}n + {:.1f}".format(slope, intercept)
    print(
        "Pot {} response curve: {}".format(
            chan+1,
            response_equation
        )
    )

    plt.scatter(inputrange, outrange, marker='.')
    plt.plot(inputrange, intercept + slope * inputrange,
        label="${}$".format(response_equation)
    )
    plt.xlabel("Input")
    plt.ylabel("$R(\\Omega)$")
    plt.ylim(ymin=0)
    plt.legend()
    plt.show()

    utils.save(settings.DATA_DIR / 'digipot' / fname, np.array([inputrange, outrange]), {})

if __name__ == "__main__":
    try:
        arg = int(sys.argv[1])
        pot_range = [arg-1]
    except (IndexError, ValueError):
        pot_range = range(6)

    for i in pot_range:
        input("Connect leads to pot {}".format(i+1))
        main(i,"pot{}response".format(i+1))