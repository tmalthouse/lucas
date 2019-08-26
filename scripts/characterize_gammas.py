import settings, utils
import numpy as np
import matplotlib.pyplot as plt
import digipot as dp
import visa
from tqdm import tqdm
import TEK_getdata as osc
from time import sleep

CHANNEL=3

def main():
    channel = int(input("Channel > "))
    rm = visa.ResourceManager()
    resources = rm.list_resources()

    scope = None
    for res in resources:
        if settings.SCOPE_ID in res:
            scope = rm.open_resource(res)
            scope.write('DAT:WID 1')
            scope.write("DAT:ENC RIB")
            scope.write("DAT:SOU CH1")
    
    if scope is None:
        raise FileNotFoundError("Could not locate scope!")
    
    with dp.DigiPot() as pot:
        digipot_settings = np.arange(256)
        Vin = np.zeros_like(digipot_settings, dtype='float')
        Vout = np.zeros_like(digipot_settings, dtype='float')
        for n in tqdm(digipot_settings):
            # tqdm.write("Setting pot")
            pot.set(channel, n)
            # tqdm.write("Set pot")
            sleep(0.05)
            ch1, ymu1 = osc.sample_channel(scope, 1)
            ch2, ymu2 = osc.sample_channel(scope, 2)
            # tqdm.write("Gathered data")
            Vin[n] = (np.max(ch1) - np.min(ch1))*float(ymu1)
            Vout[n] = (np.max(ch2) - np.min(ch2))*float(ymu2)
    
    filename = input("Savefile > ")
    utils.save(filename, np.array([digipot_settings, Vin, Vout]).T, {'channel': channel})

    scope.close()

if __name__ == "__main__":
    main()