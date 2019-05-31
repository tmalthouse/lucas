import visa
import numpy as np
import settings
import time
import sys
import math
import utils

def convert_data(rawdata):
    return np.array([x if x <= 127 else x-256 for x in map(ord,rawdata)])

def sample_channel(scope,channel):
    scope.write("DAT:SOU CH{}".format(channel))
    return convert_data(scope.query_binary_values("CURV?", datatype='c'))

def optimum_tperdiv(freq):
    return 3.0/(10*freq)

def fexp(f):
    return int(math.floor(math.log10(abs(f)))) if f != 0 else 0

def fman(f):
    return f/10**fexp(f)

# The t/div for the scope must be 1, 2.5, or 5
def scopefriendly_tperdiv(freq):
    optimum = optimum_tperdiv(freq)
    level = fexp(optimum)
    base = fman(optimum)

    if base < 1.75:
        base = 1
    elif 1.75 < base < 3.75:
        base = 2.5
    elif 3.75 < base < 7.5:
        base = 5
    else:
        base = 1
        level+=1
    
    return "{}E{}".format(base, level)


def init():
    rm = visa.ResourceManager()
    
    scope = None
    fngen = None

    resources = rm.list_resources()
    print(resources)

    for res in resources:
        opened = rm.open_resource(res)
        opened.timeout = 5000
        if settings.SCOPE_ID in res:
            scope = opened
            print("Found scope")
        elif settings.FNGEN_ID in res:
            fngen = opened
            print("Found function generator")
        else:
            print("Unknown intrument detected with id {}. Continuing...".format(res))
    
    if (scope is None or fngen is None):
        raise FileNotFoundError("Unable to locate oscilloscope and function generator")
    
    return (scope, fngen)

def set_freq(fngen, freq):
    fngen.write("FREQ {}".format(freq))

def main(min, max, step, fname):
    scope, fngen = init()

    frames = []

    print("Beginning sweep...")
    for f in np.arange(min, max, step):
        print("f={:.2f}Hz".format(f))
        set_freq(fngen, f)

        tpd = scopefriendly_tperdiv(f)
        scope.write("HOR:MAIN:SCA {}".format(tpd))

        #Let things stabilize
        time.sleep(0.05)
        ch1 = sample_channel(scope,1)
        ch2 = sample_channel(scope,2)
        frames.append(np.array([ch1,ch2]))
    print("Done w/ sweep")

    capture_metadata = {
        'fmin': min,
        'fmax': max,
        'fstep': step
    }
    utils.save(settings.DATA_DIR / "delay" / "{}".format(fname), np.array(frames), capture_metadata)
    print("Saved data. Exiting...")




if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 5:
        print("This program requires 4 arguments: min_freq, max_freq, freq_step, and filename")
        exit(-2)
    main(int(argv[1]), int(argv[2]), float(argv[3]), argv[4])