#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
import siroap_library as siroap

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
wl0         = 1.55e-6
btu_length  = 750e-6

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

N = 2   
M = 3   
DEVICE = 'cpu'
# DEVICE = torch.device("cuda")   

# Define source and detector list
src_list = [0]
#det_list = [*range(1, 8*N, 1)]
det_list = [1, 12]

# Redefine the BTU factory and pass to the Mesh network object to instantiate
def btu_factory1():
    return sip.BTU(phiU=0,phiL=0,phi_offset=0,neff=neff,ng=ng,wl0=wl0,length=btu_length, loss=btu_loss, trainable=False)

Mesh1 = siroap.SqrMesh_NxM(N,M, btu_factory1).to(DEVICE).terminate(src_list,det_list).initialize()    
print(torch.where(Mesh1.free_ports_at)[0])

# Mesh1.graph(draw=True)

# Define mesh parameters and states
kappa_p1 = 0.1
kappa_p2 = 0.1
kappa1 = np.sqrt(kappa_p1)
kappa2 = np.sqrt(kappa_p2)
theta = np.pi/4
        

mesh_dict = {'V0_0': ['coupler', kappa1],
             'V0_1': ['coupler', kappa2],
             'H0_0': ['phase_shifter_bar', theta],
             'H1_0': ['bar']
             }

for key in mesh_dict.keys():
    #print(key)
    Mesh1.sqrmesh_nxm.set_state(key, mesh_dict[key])    
    
Mesh1.initialize()
            
#print(torch.where(Mesh1().free_ports_at)[0])


# get detector outputs
det = Mesh1.forward(source=1)
 
# Use this block to plot all detector signals
# Cant do dB plots here
fig0 = plt.figure() 
Mesh1.plot(det)
plt.show()



# extract all the detectors from the circuit
det_list = [
        name for name, comp in Mesh1.components.items() if isinstance(comp, Detector)
    ]

thru = sip.dB10(det[0,:,det_list.index('p1'),0])
drop = sip.dB10(det[0,:,det_list.index('p12'),0])

fig1 = plt.figure()


plt.plot((f-fc)/GHz, thru, label='thru')
plt.plot((f-fc)/GHz, drop, label='drop')

ymin = -40
ymax = 10
plt.axis([fmin, fmax, ymin, ymax])
plt.ylabel('Transmission, dB')
plt.xlabel('frequency offset, GHz')
plt.legend(loc='lower right')
plt.show()
               