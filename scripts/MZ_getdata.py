import visa
import numpy as np
from matplotlib import pyplot as plt
import datetime
from settings import *
import array
from TEK_getdata import capturedata
import utils

dat, md = capturedata()
ch1, ch2 = dat
fname = input("Filename for data: > ")
md['MZModNum'] = input("Mach-Zehnder number: > ")
md['Power'] = input("Laser power (mA): > ")
utils.save(
    DATA_DIR / "mach_zehnder" / "{}".format(fname),
    np.array([ch1,ch2]).T,
    md
)
print("Data saved! Exiting...")
