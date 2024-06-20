#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the main SiROAP library that defines objects used in constructing the 
COB arrays

The code is copyright of Vishal Saxena, 2022 and permission and license is 
required to reuse this code.

Created on Fri Jul 30 21:17:26 2021

@author: vsaxena
"""
import numpy as np
import torch 
import photontorch as pt 

# Relative
from photontorch.components.terms import Source
from photontorch.components.terms import Detector
from photontorch.components.terms import Term
from photontorch.components  import Component
from photontorch.nn.nn import Parameter, Buffer

# Import local library
import sip_library as sip


_DEBUG = True

##############################################################################
## Square Mesh Class
##############################################################################
# Define static data for the bar and cross states
state_dict = {'bar': [np.pi, 0.],
             'cross': [0., 0.]}

def _btu_factory():
    return sip.BTU(
        phiU=0,
        phiL=0,
        neff=2.34,
        ng=3.40,
        wl0=1.55e-6,
        length=500e-6,
        loss=0.25, #dB
        trainable=True,
    )


class SqrMesh_NxM(pt.Network):
    """ A helper network for SqrMesh_NxN """    
    def __init__(self,  
            N=2, M=2, btu_factory=_btu_factory, name=None,
            ):
        """
        Args:
            N (int): number of cells in X and Y direction in the mesh.            
            btu_factory (callable): function without arguments which creates the BTUs or
                any other general 4-port component with  ports defined anti-clockwise.
            name (optional, str): name of the component
        """        
        self.N = N
        self.M = M
        # num_btus = 2*N*(N+1)
        
        # Define components
        components = {}
        
        for i in range(self.N):
            for j in range(self.M+1):
                components["V%i_%i" % (i,j)] = btu_factory()
                if (_DEBUG): print("V%i_%i created" % (i,j))

        for i in range(self.N+1):
            for j in range(self.M):
                components["H%i_%i" % (i,j)] = btu_factory()
                if (_DEBUG): print("H%i_%i created" % (i,j))

        if (_DEBUG): print(components)

        # Define connections between components
        connections = []
        
        # Connect up all the vertical BTUs to the horizontal ones       
        for i in range(self.N):
            for j in range(self.M+1):
                
                # Connect vertical BTU V(i,j) to the horizontal BTUs top-right and bottom-right
                if j < self.M :
                    connections += ["V%i_%i:3:H%i_%i:0" % (i, j, i, j)]
                    connections += ["V%i_%i:2:H%i_%i:3" % (i, j, (i+1), j)]
                
                # Connect vertical BTU V(i,j) to the horizontal BTUs top-left and bottom-left
                if j>0:
                    connections += ["V%i_%i:0:H%i_%i:1" % (i, j, i, j-1)]
                    connections += ["V%i_%i:1:H%i_%i:2" % (i, j, (i+1), j-1)]
                
                if (_DEBUG): print("Connections to V%i_%i initialized" % (i,j))
                        
        
        # Connect the optical I/O connections
        
        # West Edge connections
        for i in range(self.N):            
            connections += ["V%i_%i:0:%i" % (i, 0, 2*i)]
            connections += ["V%i_%i:1:%i" % (i, 0, 2*i+1)]
        
        if (_DEBUG): print("West Edge I/O defined")
        
        # South Edge connections    
        for j in range(self.M):                        
            connections += ["H%i_%i:0:%i" % (self.N, j, 2*self.N+2*j)]
            connections += ["H%i_%i:1:%i" % (self.N, j, 2*self.N+2*j+1)]
        
        if (_DEBUG): print("South Edge I/O defined")
                                     
        # East Edge connections
        for i in range(self.N):            
            connections += ["V%i_%i:2:%i" % (self.N-1-i, self.N, 2*(self.N+self.M)+2*i)]
            connections += ["V%i_%i:3:%i" % (self.N-1-i, self.N, 2*(self.N+self.M)+2*i+1)]            

        if (_DEBUG): print("East Edge I/O defined")
        
        # North Edge connections
        for j in range(self.M):            
            connections += ["H%i_%i:2:%i" % (0, self.M-1-j, 2*(2*self.N+self.M)+2*j)]
            connections += ["H%i_%i:3:%i" % (0, self.M-1-j, 2*(2*self.N+self.M)+2*j+1)]
         
        if (_DEBUG): print("North Edge I/O defined")
        
        if (_DEBUG): print(connections)
                
        # initialize network   
        super(SqrMesh_NxM, self).__init__(
            components, connections, name=name
        )
             
    def set_state(self, btu_key, state):
        
        if state[0] == 'bar':
            phiU = state_dict['bar'][0]
            phiL = state_dict['bar'][1]            
        elif state[0] == 'cross':
            phiU = state_dict['cross'][0]
            phiL = state_dict['cross'][1]            
        elif state[0] == 'coupler':
            phiU = 2*np.arccos(state[1]) # param = kappa
            phiL = 0            
        elif state[0] == 'phase_shifter_bar':
            phiU = state_dict['bar'][0] + state[1] # param = theta
            phiL = state_dict['bar'][1] + state[1]            
        elif state[0] == 'phase_shifter_cross':
            phiU = state_dict['cross'][0] + state[1] # param = theta
            phiL = state_dict['cross'][0] + state[1]            
        else:
            print("Bad arguments to function set_state")            
        
        self.components[btu_key].phiU.data.fill_(phiU)
        self.components[btu_key].phiL.data.fill_(phiL)
        
    def get_state(self, btu_key):
        mystate = {}
        mystate['phiU'] = self.components[btu_key].phiU.double()
        mystate['phiL'] = self.components[btu_key].phiL.double()
        mystate['phiD'] = (mystate['phiU'] - mystate['phiL'])/2
        mystate['phiA'] = (mystate['phiU'] + mystate['phiL'])/2
        # Total common mode delay
        mystate['phiC'] = (mystate['phiA'] + self.components[btu_key].phi00) % (2 * np.pi)
        return mystate
    
    def get_next_btu(self, btu_key):
        next_btu = {}
        index_list = btu_key.split('_')    
        i = int((index_list[0])[1:])
        j = int(index_list[1])
        if 'V' in btu_key:
            next_btu["UL"] = "H%i_%i" % (i, j-1)
            next_btu["UR"] = "H%i_%i" % (i, j)
            next_btu["LL"] = "H%i_%i" % (i+1, j-1)
            next_btu["LR"] = "H%i_%i" % (i+1, j)
            if j==0:
                next_btu["UL"] = 'None'
                next_btu["LL"] = 'None'
            elif j==self.M:   
                next_btu["UR"] = 'None'
                next_btu["LR"] = 'None'                
                
        if 'H' in btu_key:
            next_btu["UL"] = "V%i_%i" % (i-1, j)
            next_btu["UR"] = "V%i_%i" % (i-1, j+1)
            next_btu["LL"] = "V%i_%i" % (i, j)
            next_btu["LR"] = "V%i_%i" % (i, j+1)
            if i==0:
                next_btu["UL"] = 'None'
                next_btu["UR"] = 'None'
            elif i==self.N:   
                next_btu["LL"] = 'None'
                next_btu["LR"] = 'None'
                
        return next_btu 

    
    def get_ring_phase(self, btu_key):
        ring_phase = {}
        phase = 0
        path_exists = True
        
        if 'V' in btu_key:
            # Traverse left ring
            traversal_list = ['UL', 'LL', 'LR']
            phase, path_exists = self.get_path_phase(btu_key, traversal_list)            
            if path_exists: 
                ring_phase["left_ring"] = float(phase % (2 * np.pi))            
            # Traverse right ring
            
            traversal_list = ['UR', 'LR', 'LL']
            phase, path_exists = self.get_path_phase(btu_key, traversal_list)
            if path_exists: 
                ring_phase["right_ring"] = float(phase % (2 * np.pi))
                    
        if 'H' in btu_key:
            # Traverse upper ring
            traversal_list = ['UL', 'UR', 'LR']
            phase, path_exists = self.get_path_phase(btu_key, traversal_list)
            if path_exists:
                ring_phase["upper_ring"] = float(phase % (2 * np.pi)) 
        
            # Traverse lower ring            
            traversal_list = ['LR', 'LL', 'UL']
            phase, path_exists = self.get_path_phase(btu_key, traversal_list)
            if path_exists:
                ring_phase["lower_ring"] = float(phase % (2 * np.pi)) 
            
        return ring_phase


    def get_path_phase(self, btu_key, traversal_list):
        key = btu_key                    
        path_exists = True        
        net_phase = self.get_state(key)['phiC']
        print("Traversing path: %s" % (key))
        for direction in  traversal_list:    
            key = self.get_next_btu(key)[direction]
            print("%s" % (key))            
            if key == 'None':
                path_exists = False
            net_phase += self.get_state(key)['phiC']
        return net_phase, path_exists

        
    def terminate(self, src_list, det_list):
        """ Connect source and detector the the src_list and det_list resp.
            Rest are all terminated.
        """ 
        # src_idx = 0
        #det_idx = 0
        # term_idx = 0
        term = []
        
        for i in range(0, 4*(self.N+self.M)):
            if (i in src_list):                
                term += [Source(name="s%i" % i)]
                # src_idx += 1
            elif (i in det_list):    
                term += [Detector(name="p%i" % i)]
                #det_idx += 1
            else:
                term += [Term(name="t%i" % i)]
                # term_idx += 1

        if (_DEBUG): print(term)                
        ret = super(SqrMesh_NxM, self).terminate(term)
        ret.to(self.device)
        return ret      
###############################################################################        