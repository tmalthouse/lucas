from math import pi as π
import math as m
from collections import namedtuple

class params(object):
    def __init__(self, patch={}, **kwargs):
        # sensible defaults
        self.τ = 0.01
        self.gamma = 1.01
        self.w0 = m.sqrt(3)
        self.ep = self.w0**2
        self.THmax = 2*π/self.w0
        self.τ_sf = 1.084*self.THmax
        self.r = 0.25
        self.τ_c = self.τ * self.τ_sf
        self.ξ = self.τ_c/self.τ_sf
        self.φ = 0

        self.__dict__.update(patch)
        self.__dict__.update(kwargs)
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__dict__.__repr__()

class illing_params(params):
    def __init__(self, patch={}, **kwargs):
        super().__init__(patch, **kwargs)
        # Change any defaults here:

        # And finally, apply user-requested changes
        self.__dict__.update(kwargs)

class mhouse_params(params):
    def __init__(self, patch={}, **kwargs):
        super().__init__()
        # Change any defaults here:
        self.w0 = m.sqrt(2)
        self.THmax = 2*π/self.w0
        self.ξ = 1e-4
        self.τ_sf = 200/self.THmax
        self.τ_c = self.ξ * self.τ_sf

        # And finally, apply user-requested changes
        self.__dict__.update(kwargs)

class bao_params(params):
    def __init__(self, patch={}, **kwargs):
        super().__init__(patch, **kwargs)
        self.ξ = 5e-4
        self.w0 = 8.358/1.864
        self.r = 3.58
        self.ep = self.w0**2

        self.τ = 1.1
        self.THmax = 2*π/self.w0
        self.omega_0 = self.w0 * 2 * π

        self.τ_sf = self.τ * (2*π/self.omega_0)
        self.τ_c = self.τ_sf * self.ξ

        # And finally, apply user-requested changes
        self.__dict__.update(kwargs)


default = bao_params