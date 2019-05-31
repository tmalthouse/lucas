import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import sys
import settings
import utils

def phasediff(ch1,ch2, freq):
    #First adjust both to be centered at 0
    ch1 = ch1.astype(float) - np.mean(ch1)
    ch2 = ch2.astype(float) - np.mean(ch2)
    tdata = np.arange(2500)

    def fnform(t, a, b, c):
        return a * np.sin(b*t + c)
    
    omega = 0.0062
    ch1fit,_ = curve_fit(fnform, tdata, ch1, [100,omega,0])
    ch2fit,_ = curve_fit(fnform, tdata, ch2, [100,omega,0])

    # print("CH1 fit {} CH2 fit {}".format(ch1fit, ch2fit))

    # plt.scatter(tdata, ch1, marker='.')
    # plt.plot(tdata, fnform(tdata, ch1fit[0], ch1fit[1], ch1fit[2]))
    # plt.scatter(tdata, ch2, marker='.')
    # plt.plot(tdata, fnform(tdata, ch2fit[0], ch2fit[1], ch2fit[2]))
    # plt.show()

    ch1phase = ch1fit[2]
    ch2phase = ch2fit[2]
    return (ch1phase-ch2phase) % (2 * np.pi)

def main(data, base, step):
    freqs = np.arange(base, base + len(data)*step, step)
    # print(len(freqs))
    phasediffs = np.zeros(len(data))
    # print(len(phasediffs))
    
    for f in range(len(data)):
        dat = data[f]
        ch1 = dat[0]
        ch2 = dat[1]
        phasediffs[f] = phasediff(ch1,ch2, freqs[f])
    
    def cos2fnform(f, a, b, c):
        return a * np.cos(b*f + c)**2

    cos2fit,_ = curve_fit(cos2fnform, freqs, np.cos(phasediffs)**2)

    # plt.scatter(freqs, phasediffs)
    plt.scatter(freqs, np.cos(phasediffs)**2)
    plt.plot(freqs, cos2fnform(freqs, *cos2fit), label="$\\Delta \\phi = {:.2f}*f + {:.2f}$".format(cos2fit[1], cos2fit[2]%(2*np.pi)))
    plt.xlabel("$f$(Hz)")
    plt.ylabel("$\\cos^2(\\Delta \\phi)$")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print("Need a datafile to run on")
        sys.exit(2)
    
    data, md = utils.load(settings.DATA_DIR / "delay" / "{}".format(argv[1]))
    main(data, md['fmin'], md['fstep'])