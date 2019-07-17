from math import pi as π
import math as m
from collections import namedtuple

class params(object):
    def __init__(self, **kwargs):
        # sensible defaults
        self.tau = 0.01
        self.gamma = 1.01
        self.w0 = m.sqrt(3)
        self.ep = self.w0**2
        self.THmax = 2*π/self.w0
        self.tau_sf = 1.084*self.THmax
        self.r = 0.25
        self.tau_c = self.tau * self.tau_sf
        self.x_i = self.tau_c/self.tau_sf
        self.phi = 0

        # If we want to change or add any parameters
        self.__dict__.update(kwargs)
        