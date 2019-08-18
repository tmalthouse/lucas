import serial
from time import sleep
import IPython

linux_serialport = '/dev/ttyACM0'
osx_serialport = ['/dev/cu.usbmodem14101','/dev/cu.usbmodem14201']

class DigiPot(object):
    def __init__(self):
        pass
    
    def __enter__(self):
        print("Connecting to DigiPot...")
        self.port = None
        for p in osx_serialport:
            try:
                self.port = serial.Serial(p, 9600, timeout=3)
            except serial.serialutil.SerialException:
                pass
        if self.port is None:
            raise serial.serialutil.SerialException("Plug in arduino!")
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
        # print("Writing {:x}  to {:x}.".format(val, chan))
        pkt = bytearray([
                chan, val, 0x0A
            ])

        self.port.write(
            pkt
        )
        # print(f"raw=[{list(map(int,pkt))}]")
        rawline = self.port.readline()
        line = rawline.decode('ascii').rstrip()
        if (line == "A"):
            pass # Success!
        elif (line == "B"):
            raise IOError("Circuit power is not on!")
        elif (line == "C"):
            raise IOError(f"Malformed command! ([{rawline}])")
        else:
            raise IOError(f"Unknown return code {line}")
        



class DigiPotDummy(object):
    def __init__(self):
        print(f"{'*'*41}\nDigiPot controller running in dummy mode!\n{'*'*41}\n")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def set(self, chan, val):
        pass

if __name__ == "__main__":
    with DigiPot() as dp:
        IPython.embed()
