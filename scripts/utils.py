import numpy as np
import json
import os.path
import datetime

def dict_to_arr(metadata):
    return np.array(list(metadata.items()))

def arr_to_dict(arr):
    d = {}
    for a in arr:
        d[a[0]] = tryparse(a[1])
    return d

def tryparse(f):
    try:
        return float(f)
    except ValueError:
        return f

def save(file, arr, metadata={}):
    # Add a capture timestamp
    metadata['captime'] = datetime.datetime.now().isoformat()
    # Save both in a single compressed file
    np.savez_compressed("{}.npz".format(file), data=arr, md=dict_to_arr(metadata))

def load(file):
    # If the file is the newer compressed, all-in-one.
    # This block is first, since we prefer the newer format
    # if both exist
    if os.path.isfile("{}.npz".format(file)):
        with np.load("{}.npz".format(file)) as datafile:
            data = datafile['data']
            metadata = arr_to_dict(datafile['md'])
    
    # If the data is an old-style npy/dat combo
    elif os.path.isfile("{}.npy".format(file)):
        print("Old-style (npy/dat) combo file detected! Converting...")
        data = np.load("{}.npy".format(file))
        with open("{}.dat".format(file), "r") as datfile:
            metadata = json.load(datfile)
            # print("metadata = {}".format(metadata))
        save(file, data, metadata)
        print("Converted. This file will now load faster in the future.")

    else:
        raise FileNotFoundError

    return data, metadata

def convertfile(file):
    f = load(file)
    save(file, *f)
