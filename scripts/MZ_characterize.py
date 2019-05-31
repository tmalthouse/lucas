from settings import *
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.optimize import curve_fit

def raw_to_volts(series, mult):
    return series * mult




def main(argv):
    if (len(argv) != 2):
        print("Need to supply filename!")
        sys.exit(2)
    data = np.load(DATA_DIR / "mach_zehnder" / "{}.npy".format(argv[1])).astype('float').T

    with open(DATA_DIR / "mach_zehnder" / "{}.dat".format(argv[1]), "r", encoding='utf8') as capdatfile:
        capdata = json.load(capdatfile)

    print(data)

    Vout = raw_to_volts(data[0], capdata['Ch1Mult'])
    Vin = raw_to_volts(data[1], capdata['Ch2Mult'])

    # The MZ clamps the minimum to 0, so fix the data to account for that
    Vout = Vout - np.min(Vout)


    print("Fitting to function Vout = a * sin^2(b * Vin + c)")

    params,_ = curve_fit(
        lambda Vin, a, b, c: a * np.sin(b*Vin + c)**2,
        Vin,
        Vout
    )

    def create_fitted_fn(params):
        def out(Vin):
            return params[0] * np.sin(params[1]*Vin + params[2])**2
        
        return out
    
    outfn = create_fitted_fn(params)

    print("Fitted Results:\n\ta={}\n\tb={}\n\tc={}\n\t==>Vπ={}".format(*params, np.pi/(2*params[1])))
    
    plt.scatter(Vin, Vout, marker='.')
    fnrange = np.arange(-5,5,0.05)

    plt.plot(fnrange, outfn(fnrange), color='orange',
        label="$V_{{out}} = {:.2f} \sin^2({:.3f} V_{{in}} + {:.3f})$".format(*params)
    )
    plt.legend(loc='upper right')

    plt.title("Mach-Zehnder Modulator {} Reponse Curve".format(capdata['MZModNum']))
    plt.xlabel(r"$V_{in}$")
    plt.ylabel(r"$V_{out}$")
    plt.savefig(FIG_DIR / "mach_zehnder" / "MZ{}Response.pdf".format(capdata['MZModNum']))
    plt.show()


if __name__ == "__main__":
    main(sys.argv)