def convert_data(rawdata):
    return np.array([x if x <= 127 else x-256 for x in map(ord,rawdata)])

def sample_channel(scope,channel):
    scope.write("DAT:SOU CH{}".format(channel))
    return convert_data(scope.query_binary_values("CURV?", datatype='c'))