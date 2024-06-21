#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The code is copyright of Vishal Saxena, 2022 and permission and license is 
required to reuse this code.

Created on Fri Jul 30 21:17:26 2021

@author: vsaxena
"""
#%matplotlib inline

###############################################################################
## Imports
###############################################################################
import numpy as np
import sys
import matplotlib.pyplot as plt
#plt.rcParams['text.usetex'] = True

import torch
import photontorch as pt

# setting path
sys.path.append('../siroap_libs/')

# Import local library
import sip_library as sip
# import siroap_library as siroap

# Relative
from photontorch.components.terms import Source
from photontorch.components.terms import Detector
from photontorch.components.terms import Term


###############################################################################
c           = 3e8 # speed of light
wg_loss     = 2.5 # dB/cm
btu_loss    = 0.25 # dB
ng          = 4.24 # group index
neff        = 2.34 # effective index
wl0         = 1.55e-6   # Wavelength
btu_length  = 750e-6    # BTU effective optical length
phi_offset  = np.pi*0  # Random offset in the BTU, See ISSCC 2023 paper for definition

# Simualation Parameters
GHz = 1e9
size = 1001
fmin = 0 # GHz
fmax = 50 # GHz

# detector list for plotting
det_list = []


###############################################################################
# Define the simulation environment:
freq = GHz*np.linspace(fmin, fmax, size) # frequency offset points
fc = (c/(ng*wl0))                             # reference frequency
f = fc * np.linspace(1, 1, size) + freq  # actual frequency points

env = pt.Environment(
    #wavelength = 1e-6*np.linspace(1.50, 1.501, 10001), #[m]
    f = f,
    freqdomain=True, # we will be doing frequency domain simulations
)

# set the global simulation environment:
pt.set_environment(env)
#pt.current_environment()

###############################################################################

DEVICE = 'cpu'
# DEVICE = torch.device("cuda")   

# Define source and detector list
#src_list = [0]
#det_list = [1]

# Instantiate the BTU from SiP Library
class Network2x2(pt.Network):
    def __init__(self,
            phiU,
            phiL,
            phi_offset,
            neff,
            ng,
            wl0,
            length,
            loss):
        super(Network2x2, self).__init__()
        self.s1 = pt.Source()
        self.s2 = pt.Term()
        self.d1 = pt.Detector()
        self.d2 = pt.Detector()
        self.btu = sip.BTU(phiU=phiU, phiL=phiL, phi_offset=phi_offset, neff=neff, ng=ng, wl0=wl0, length=length, loss=loss, trainable=True)
        self.link('s1:0', '0:btu:1', '0:d1')
        self.link('s2:0', '3:btu:2', '0:d2')

circuit1 = Network2x2(phiU=0,phiL=0,phi_offset=phi_offset,neff=neff,ng=ng,wl0=wl0,length=btu_length, loss=btu_loss)

# get detector outputs
det = circuit1(source=1)

print(torch.where(circuit1.free_ports_at)[0])

fig1 = plt.figure()

det_list = [
        name for name, comp in circuit1.components.items() if isinstance(comp, Detector)
    ]

theta_range = np.arange(0,np.pi,np.pi/50)
size = theta_range.shape[0]
d1 = np.zeros(size)
d2 = np.zeros(size)

wl0 = 1.5e-6

# Using frequeny domain response otherwise need to wait for long time due to the
# switch delay
with pt.Environment(wl=wl0,freqdomain=True):
    for idx, theta_i in enumerate(theta_range):
        circuit1.btu.phiU.data.fill_(theta_i)
        circuit1.btu.phiL.data.fill_(-theta_i)
        # data = [theta_i/2, -theta_i/2]
        # for i, param in enumerate(circuit1.parameters()):
        #       param.data.fill_(data[i])
        circuit1.initialize()
        #print(circuit1.btu.phiU, circuit1.btu.phiL)
        det1 = circuit1(source=1)[-1,0,:,0]
        d1[idx] = det1[0]
        d2[idx] = det1[1]
        #print(d1[idx], d2[idx])

plt.plot(theta_range/np.pi, d1, label='Data1')
plt.plot(theta_range/np.pi, d2, label='Data2')
plt.ylabel('Transmission (a.u.)')
plt.xlabel('Theta/pi, rad')
plt.legend(loc='lower right')
plt.show()

               