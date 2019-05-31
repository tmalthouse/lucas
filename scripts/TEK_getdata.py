import visa
import numpy as np
from matplotlib import pyplot as plt
import datetime
from settings import *
import array

# visa.log_to_screen()

plt.style.use('seaborn-dark')


def printquery(q):
    print("{}: {}".format(q,scope.query(q)))

def convert_data(rawdata):
    return np.array([x if x <= 127 else x-256 for x in map(ord,rawdata)])

def sample_channel(channel):
    scope.write("DAT:SOU CH{}".format(channel))
    printquery('WFMP:YMU?')
    return convert_data(scope.query_binary_values("CURV?", datatype='c'))

def save_data(data, name=None):
    param = scope.query("WFMP?")
    if name == None:
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("Saved as 'data/{}.npy".format(name))
    np.save(DATA_DIR / "mach_zehnder" / "{}.npy".format(name), data)
    

def take_measurement(name = None):
    data = np.array([sample_channel(1),sample_channel(2)])
    save_data(data, name)

def capturedata():
    rm = visa.ResourceManager()

    print("Connecting to scope...")
    try:
        scope = rm.open_resource(rm.list_resources()[0])
    except IndexError:
        print("Could not find scope---is it on and plugged in?")
        raise FileNotFoundError
    print("Connected!")
    scope.timeout = 10000

    print("Setting transfer params...")
    scope.write('DAT:WID 1')
    scope.write("DAT:ENC RIB")

    scope.write("DAT:SOU CH1")
    print("Set!")


    print("Taking data...")
    ch1 = sample_channel(1)
    ch2 = sample_channel(2)
    print("Data collected!")
    scope.close()

    return (ch1,ch2)