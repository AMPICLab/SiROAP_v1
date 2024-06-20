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
plt.rcParams['text.usetex'] = False

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
fmin = 10 # GHz
fmax = 21 # GHz

# detector list for plotting
det_list = []


_DEBUG = False

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

N = 4   
M = 4   
DEVICE = 'cpu'
# DEVICE = torch.device("cuda")   

# Define source and detector list
src_list = [30]
#det_list = [*range(1, 8*N, 1)]
det_list = [31, 5]

# Redefine the BTU factory and pass to the Mesh network object to instantiate
def btu_factory1():
    return sip.BTU(phiU=0,phiL=0,neff=neff,ng=ng,wl0=wl0,length=btu_length, loss=btu_loss, trainable=False)

Mesh1 = siroap.SqrMesh_NxM(N,M, btu_factory1).to(DEVICE).terminate(src_list,det_list).initialize()    
print(torch.where(Mesh1.free_ports_at)[0])

# Mesh1.graph(draw=True)

# Define 2nd order CROW parameters
# kappa1       = 0.36 # Coupling coefficients            
# kappa2       = 0.0685 # Coupling coefficients            
# kappa3       = 0.36 # Coupling coefficients            
kappa1       = 0.36 # Coupling coefficients            
kappa2       = 0.0685 # Coupling coefficients            
kappa3       = kappa1 # Coupling coefficients   
phi1         = 0 # Phase shifts in the rings
phi2         = 0 # Phase shifts in the rings
phi2         = 0 # Phase shifts in the rings
kappa_drop  = float(1/100) # Drop port kappa, 1% monitor tap            
            
# Map filter parameters to the mesh states
mesh_dict = {'V0_0': ['phase_shifter_bar', phi1],
             'V0_1': ['bar'],
             'V0_2': ['cross'],
             'V0_3': ['cross'],
             'V0_4': ['cross'],
             'V1_0': ['phase_shifter_bar', phi2],
             'V1_1': ['bar'],
             'V1_2': ['cross'],
             'V1_3': ['cross'],
             'V1_4': ['cross'],
             'V2_0': ['cross'],
             'V2_1': ['cross'],
             'V2_2': ['cross'],
             'V2_3': ['cross'],
             'V2_4': ['cross'],
             'V3_0': ['cross'],
             'V3_1': ['cross'],
             'V3_2': ['cross'],
             'V3_3': ['cross'],
             'V3_4': ['cross'],
             #######################
             'H0_0': ['coupler', kappa1],
             'H0_1': ['cross'],
             'H0_2': ['cross'],
             'H0_3': ['cross'],
             'H1_0': ['coupler', kappa2],
             'H1_1': ['cross'],
             'H1_2': ['cross'],
             'H1_3': ['cross'],
             'H2_0': ['coupler', kappa3],
             'H2_1': ['cross'],
             'H2_2': ['cross'],
             'H2_3': ['cross'],
             'H3_0': ['cross'],
             'H3_1': ['cross'],
             'H3_2': ['cross'],
             'H3_3': ['cross'],
             'H4_0': ['cross'],
             'H4_1': ['cross'],
             'H4_2': ['cross'],
             'H4_3': ['cross'],
             }

for key in mesh_dict.keys():
    # if _DEBUG: print(key)
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

thru = sip.dB10(det[0,:,det_list.index('p31'),0])
drop = sip.dB10(det[0,:,det_list.index('p5'),0])


fig1 = plt.figure()


plt.plot((f-fc)/GHz, thru, label='thru')
plt.plot((f-fc)/GHz, drop, label='drop')

ymin = -50
ymax = 10
plt.axis([fmin, fmax, ymin, ymax])
plt.ylabel('Transmission, dB')
plt.xlabel('frequency offset, GHz')
plt.legend(loc='lower right')
plt.show()
                              