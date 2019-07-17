import utils
import settings
import numpy as np
import math
import digipot
from os import system

BRIDGE_R = 33000

wiper_r = 31.67
step_r = 202.35
possible_Rs = wiper_r + step_r * np.arange(256)
# print(np.array([np.arange(256),possible_Rs]).T)

command_listing = """Available Commands:

(1) Loop 1 self-feedback
(2) Loop 1->Loop 2 coupling
(3) Loop 2 self-feedback
(4) Loop 2->Loop 1 coupling
(?) Display help
(q) Exit
"""

channel_map = {
    1: 4,
    2: 3,
    3: 2,
    4: 5
}

def gain(R):
    return BRIDGE_R/R

def gain_to_R(gain):
    return BRIDGE_R/gain

def closest_possible_r(R):
    idx = np.searchsorted(possible_Rs, R)
    if idx > 0 and (idx == len(possible_Rs) or math.fabs(R - possible_Rs[idx-1]) < math.fabs(R - possible_Rs[idx])):
        return idx, possible_Rs[idx-1]
    else:
        return idx, possible_Rs[idx]

def setgain(g, chan, dp):
    needed_r = gain_to_R(g)
    setting, actual_r = closest_possible_r(needed_r)
    print("Setting = 0x{:x}, actual R = {:.2f}".format(setting, actual_r))
    print("Actual gain = {:.2f}".format(gain(actual_r)))
    dp.set(chan, setting)

def querygain(dp, chan):
    gain_s = input("Desired gain for channel {}: ".format(chan))
    try:
        gain = float(gain_s)
        if gain < 0:
            raise ValueError
        else:
            setgain(gain, channel_map[chan], dp)
    except ValueError:
        print("Invalid gain {}. Must be positive.".format(gain_s)) 

def main():
    with digipot.DigiPotDummy() as dp:
        print("Gain Control System")
        print(command_listing)
        while (True):
            a = input('> ').strip()
            if a == 'q':
                break
            elif a == '?':
                print(command_listing)
                continue
            elif a[0] == '!':
                system(a[1:])
            else:
                try:
                    chan = int(a)
                    if (chan < 1 or chan > 4):
                        raise ValueError
                    else:
                        querygain(dp,chan)
                except ValueError:
                    print("Unknown option '{}'.".format(a))

if __name__ == "__main__":
    main()