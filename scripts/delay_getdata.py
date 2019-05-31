import visa
import numpy as np
from matplotlib import pyplot as plt
import datetime
from settings import *
import array
from TEK_getdata import capturedata

ch1,ch2 = capturedata()
fname = input("Filename for data: > ")
np.save(
    DATA_DIR / "mach_zehnder" / "{}.npy".format(fname),
    np.array([ch1,ch2]).T
)
print("Data saved! Exiting...")
