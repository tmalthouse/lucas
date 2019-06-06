import serial
from time import sleep
import IPython

linux_serialport = '/dev/ttyACM0'
osx_serialport = '/dev/cu.usbmodem14101'

class DigiPot(object):
    def __init__(self):
        pass
    
    def __enter__(self):
        self.port = serial.Serial(osx_serialport, 9600, timeout=3)
        #Clean out any crud in the serial pipe
        try:
            self.set(-1,1)
        except IOError:
            pass
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.port.close()
    
    def set(self, chan, val):
        self.port.reset_input_buffer()
        self.port.write(
            "{} {};".format(chan, val).encode('ascii')
        )
        sleep(0.1)
        line = self.port.readline().decode('ascii').rstrip()
        # print("Returned line is '{}'".format(line))
        if (line != "OK;"):
            raise IOError("Bad return code: '{}'. Expected 'OK;'".format(line))


if __name__ == "__main__":
    with DigiPot() as dp:
        IPython.embed()