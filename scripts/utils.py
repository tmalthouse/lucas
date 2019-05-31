import numpy as np
import json

def save(file, arr, metadata):
    np.savez_compressed("{}.npy".format(file), arr)
    with open("{}.dat".format(file), "w") as datfile:
        json.dump(metadata, datfile)

def load(file):
    data = np.load("{}.npy".format(file))
    with open("{}.dat".format(file), "r") as datfile:
        metadata = json.load(datfile)
    return data, metadata