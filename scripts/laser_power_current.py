import numpy as np
import json
import sys, getopt
from scipy.stats import linregress

import matplotlib.pyplot as plt

def main(argv):
    if (len(argv) != 3):
        print("Call as {} laser.dat laser_IV_response.csv".format(argv[0]))
        sys.exit(2)
    
    
    with open(argv[1], "r") as laserdat:
        laserdata = json.load(laserdat)
    
    ivcurve = np.genfromtxt(argv[2], delimiter=',')[1:] #Get rid of the header line

    currents, voltages = ivcurve.T

    powers = voltages /( laserdata['R'] * laserdata['G'])

    lin_currents = currents[powers>0.01]
    lin_powers = powers[powers>0.01]

    slope, intercept, R2, _, stderr = linregress(lin_currents, lin_powers)

    def est_power(current):
        return intercept + slope*current

    threshold_current = -intercept/slope
    print(threshold_current)

    print("R2 = {:.2f}, stderr = {:.2f}".format(R2, stderr))

    expected_slope, expected_curve = specsheetcurve(laserdata)

    print("Expected slope = {:.2f}mW/mA\nActual slope = {:.2f}mW/mA \nRatio = {:.2f}".format(
        expected_slope, slope, expected_slope/slope
    ))

    plt.scatter(currents, powers, marker='.')
    plt.plot(lin_currents, est_power(lin_currents), label="Measured Slope")
    plt.plot(lin_currents, expected_curve(lin_currents), label="Expected Slope")
    plt.xlabel("Current (mA)")
    plt.ylabel("Laser power (mW)")
    plt.legend()
    plt.show()

    resids = lin_powers - est_power(lin_currents)

    plt.scatter(lin_currents, resids, marker='.')
    plt.xlabel("Current (mA)")
    plt.ylabel("Residual")
    plt.show()

def specsheetcurve(laserdata):
    slope = 40/(laserdata["OpCurrent"] - laserdata["Threshold"])
    intercept = -slope * laserdata["Threshold"]
    
    return slope, lambda I: intercept + slope*I

if __name__ == "__main__":
    main(sys.argv)