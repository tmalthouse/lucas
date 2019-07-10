import serial
from time import sleep
import IPython

linux_serialport = '/dev/ttyACM0'
osx_serialport = '/dev/cu.usbmodem14201'

class DigiPot(object):
    def __init__(self):
        pass
    
    def __enter__(self):
        print("Connecting to DigiPot...")
        self.port = serial.Serial(osx_serialport, 9600, timeout=3)
        #Clean out any crud in the serial pipe, by (purposefully) triggering an error
        try:
            self.set(10,1)
        except IOError:
            pass
        print("Connected")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.port.close()
    
    def set(self, chan, val):
        # self.port.reset_input_buffer()
        # print("Writing {}  to {}.".format(val, chan))
        self.port.write(
            bytearray([
                chan, val, 0x0A
            ])
        )
        line = self.port.readline().decode('ascii').rstrip()
        if (line != "A"):
            raise IOError("Bad return code: '{}'. Expected 'A'".format(line))


if __name__ == "__main__":
    with DigiPot() as dp:
        IPython.embed()