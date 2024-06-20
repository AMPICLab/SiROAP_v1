#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is SiROAP GUI library that defines graphics for the BTUs 

The code is copyright of Vishal Saxena, 2022 and permission and license is 
required to reuse this code.
Created on Fri Jul 30 21:17:26 2021

@author: vsaxena
"""

import numpy as np
import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem, QApplication, QGraphicsItem, QGraphicsItemGroup, QGraphicsPathItem
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter, QPainterPath
from PyQt5.QtCore import Qt


_DEBUG = True

app = QApplication(sys.argv)


orange = QColor(255,165,0)
skyblue = QColor(53,91,92)


#group = QGraphicsItemGroup()
#group.setFlag(QGraphicsItem.ItemIsMovable) #let't test how it works

class BTU_group(QGraphicsItemGroup):
    def __init__(self, state, rectw, recth, termlen):
        super().__init__()        
        # Heaters        
        global orange
        #self.state = ['cross'] 
        self.state = state
        self.WGcolor =  Qt.blue
        self.WGthickness = 1
        self.WG2color =  Qt.gray
        self.WG2thickness = 1
        self.kappa = 1
        #               
        if self.state[0] == 'cross':
            self.boxcolor =  Qt.yellow            
        elif self.state[0] == 'bar':
            self.boxcolor =  orange                          
        elif self.state[0] == 'coupler':
            self.boxcolor =  Qt.green                          
        elif self.state[0] == 'phase_shifter_bar':
            self.boxcolor =  Qt.red                          
        elif self.state[0] == 'phase_shifter_cross':
            self.boxcolor =  Qt.magenta                          
        else:
            print("Bad arguments to function BTU type")            
        #    
        self.rectw = rectw
        self.recth = recth
        self.termlen = termlen        
        self.rect1 = QGraphicsRectItem(self.termlen, 0, self.rectw, self.recth)        
        self.brush1 = QBrush(self.boxcolor)
        self.rect1.setBrush(self.brush1)        
        pen1 = QPen(self.WGcolor)
        pen1.setWidth(self.WGthickness)
        self.rect1.setPen(pen1)        
        self.addToGroup(self.rect1) 
        self.line1 = QGraphicsLineItem(0,self.recth/4,self.termlen,self.recth/4)
        self.line2 = QGraphicsLineItem(0,self.recth*3/4,self.termlen,self.recth*3/4)
        self.line3 = QGraphicsLineItem(self.rectw+self.termlen,self.recth/4,self.rectw+2*self.termlen,self.recth/4)
        self.line4 = QGraphicsLineItem(self.rectw+self.termlen,self.recth*3/4,self.rectw+2*self.termlen,self.recth*3/4)
        self.line1.setPen(pen1)        
        self.line2.setPen(pen1)        
        self.line3.setPen(pen1)        
        self.line4.setPen(pen1)        
        self.addToGroup(self.line1)         
        self.addToGroup(self.line2)         
        self.addToGroup(self.line3)         
        self.addToGroup(self.line4)         
        # Draw Arcs
        self.arc1 = QGraphicsEllipseItem(-self.recth/4, -self.recth/4, self.recth/2, self.recth/2)
        self.arc1.setStartAngle(180*16)
        self.arc1.setSpanAngle(360*4)
        self.arc1.setPen(pen1)
        self.addToGroup(self.arc1) 
        self.arc2 = QGraphicsEllipseItem(-self.recth/4+self.termlen*2+self.rectw, -self.recth/4, self.recth/2, self.recth/2)
        self.arc2.setStartAngle(270*16)
        self.arc2.setSpanAngle(360*4)
        self.arc2.setPen(pen1)
        self.addToGroup(self.arc2) 
        self.arc3 = QGraphicsEllipseItem(-self.recth/4+self.termlen*2+self.rectw, -self.recth/4+self.recth, self.recth/2, self.recth/2)
        self.arc3.setStartAngle(0*16)
        self.arc3.setSpanAngle(360*4)
        self.arc3.setPen(pen1)
        self.addToGroup(self.arc3)
        self.arc4 = QGraphicsEllipseItem(-self.recth/4, -self.recth/4++self.recth, self.recth/2, self.recth/2)
        self.arc4.setStartAngle(90*16)
        self.arc4.setSpanAngle(360*4)
        self.arc4.setPen(pen1)
        self.addToGroup(self.arc4)
        
        #  Create the bar and cross lines             
        pen2 = QPen(self.WG2color)
        pen2.setWidth(self.WG2thickness)
        if self.state[0] == 'cross' or self.state[0] == 'phase_shifter_cross':            
            self.lineA = QGraphicsLineItem(self.termlen,self.recth/4,self.rectw+self.termlen,self.recth*3/4)              
            self.lineB = QGraphicsLineItem(self.termlen,self.recth*3/4,self.rectw+self.termlen,self.recth/4)             
            self.lineA.setPen(pen2)        
            self.addToGroup(self.lineA)         
            self.lineB.setPen(pen2)        
            self.addToGroup(self.lineB)                    
        elif self.state[0] == 'bar' or self.state[0] == 'phase_shifter_bar':
            self.lineA = QGraphicsLineItem(self.termlen,self.recth/4,self.rectw+self.termlen,self.recth/4)              
            self.lineB = QGraphicsLineItem(self.termlen,self.recth*3/4,self.rectw+self.termlen,self.recth*3/4)             
            self.lineA.setPen(pen2)        
            self.addToGroup(self.lineA)         
            self.lineB.setPen(pen2)        
            self.addToGroup(self.lineB)                     
        elif self.state[0] == 'coupler':            
            self.text1 = QGraphicsTextItem("%d" %(self.kappa))  
            self.addToGroup(self.text1)                                   
        else:
            print("Bad arguments to function BTU type")            
        #
class opIO_group(QGraphicsItemGroup):    
    def __init__(self, rectw, recth, termlen, WGthickness, name):
        super().__init__()                
        self.rectw = rectw
        self.recth = recth
        self.termlen = termlen
        self.WGthickness = WGthickness
        self.name = name
        #
        self.WGcolor = Qt.blue        
        self.boxcolor =  Qt.cyan
        self.rect1 = QGraphicsRectItem(-self.rectw-self.termlen, -self.recth/2, self.rectw, self.recth)        
        self.brush1 = QBrush(self.boxcolor)
        self.rect1.setBrush(self.brush1)        
        pen1 = QPen(self.WGcolor)
        pen1.setWidth(self.WGthickness)
        self.rect1.setPen(pen1)        
        self.addToGroup(self.rect1) 
        self.line1 = QGraphicsLineItem(-self.termlen, 0, 0, 0)        
        self.line1.setPen(pen1)                
        self.addToGroup(self.line1)         
        #
        self.text = QGraphicsTextItem(name)
        self.text.setPos(0,0)
        #self.text.setAlignment(AlignLeft())
        self.addToGroup(self.rect1) 
    

###############################################################################
class MeshGraphicsScene(QGraphicsScene):    
    def __init__(self, N, M, mesh_dict):
        super().__init__(0, 0, 1200, 1200)        
        # Define Scene
        #scene = QGraphicsScene(0, 0, 1200, 1200)
        
        # Define BTU and Mesh Graphics
        BTUs = {}  
        btu_rectw = 40
        btu_recth = 25
        btu_termlen = 20 
        btu_tot_len = btu_rectw + 2*btu_termlen + 0.5*btu_recth
        for key in mesh_dict.keys():
            # if _DEBUG: print(key)
            state = mesh_dict[key] 
            BTUs[key] = BTU_group(state, btu_rectw, btu_recth, btu_termlen)
            
        xpitch = btu_rectw + 2*btu_termlen + btu_recth  #140
        ypitch = xpitch #140
        x0 = 200
        y0 = 100
        xoffsetV = x0
        yoffsetV = btu_recth + y0
        xoffsetH = x0
        yoffsetH = y0
                
        for i in range(N):
            for j in range(M+1):
                key = "V%i_%i" % (i,j)
                #BTUs[key] = BTU_group()
                self.addItem(BTUs[key])
                BTUs[key].setRotation(90) 
                BTUs[key].rect1.setData(0, key)         
                BTUs[key].setPos(xoffsetV+j*xpitch, yoffsetV+i*ypitch)
                if (_DEBUG): print("V%i_%i drawn" % (i,j))
                        
        for i in range(N+1):
            for j in range(M):
                key = "H%i_%i" % (i,j)
                #BTUs[key] = BTU_group()
                self.addItem(BTUs[key])
                BTUs[key].rect1.setData(0, key)          
                BTUs[key].setPos(xoffsetH+j*xpitch, yoffsetH+i*ypitch)
                if (_DEBUG): print("H%i_%i drawn" % (i,j))
        
        # Define OpticalIOs
        opIOs= {}
        opio_rectw = 30
        opio_recth = 10
        opio_termlen = 40
        opio_WGthickness = 1
        
        # West and East IOs
        for i in range(2*N):
            key = "W%i" %(i)
            name = key # Can replace by a dictionary later for custom labels
            opIOs[key] = opIO_group(opio_rectw, opio_recth, opio_termlen, opio_WGthickness, name)
            opIOs[key].rect1.setData(0, name)         
            key = "E%i" %(i)
            name = key # Can replace by a dictionary later for custom labels    
            opIOs[key] = opIO_group(opio_rectw, opio_recth, opio_termlen, opio_WGthickness, name)
            opIOs[key].rect1.setData(0, name)         
        # North and South IOs
        for i in range(2*M):
            key = "N%i" %(i)
            name = key # Can replace by a dictionary later for custom labels
            opIOs[key] = opIO_group(opio_rectw, opio_recth, opio_termlen, opio_WGthickness, name)
            opIOs[key].rect1.setData(0, name)         
            key = "S%i" %(i)
            name = key # Can replace by a dictionary later for custom labels
            opIOs[key] = opIO_group(opio_rectw, opio_recth, opio_termlen, opio_WGthickness, name)
            opIOs[key].rect1.setData(0, name)         
        
        
        # Draw optical IOs - East and West faces
        opio_west_xoffset = x0 - btu_recth
        opio_west_yoffset = y0 + 0.75*btu_recth
        #opio_east_xoffset = x0 + M*(btu_rectw+2*btu_termlen) + (M+1)*btu_recth 
        opio_east_xoffset = x0 + M*xpitch
        opio_east_yoffset = opio_west_yoffset
        
        for i in range(M):
            # West Edge
            key = "W%i" % (2*i)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(0)     
            opIOs[key].setPos(opio_west_xoffset, opio_west_yoffset+i*ypitch)
            if (_DEBUG): print("W%i drawn" % (2*i))
            key = "W%i" % (2*i+1)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(0)     
            opIOs[key].setPos(opio_west_xoffset, opio_west_yoffset+i*ypitch+btu_tot_len)
            if (_DEBUG): print("W%i drawn" % (2*i+1))
            #
            # East Edge
            key = "E%i" % (2*i)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(180)     
            opIOs[key].setPos(opio_east_xoffset, opio_east_yoffset+i*ypitch)
            if (_DEBUG): print("E%i drawn" % (2*i))
            key = "E%i" % (2*i+1)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(180)     
            opIOs[key].setPos(opio_east_xoffset, opio_east_yoffset+i*ypitch+btu_tot_len)
            if (_DEBUG): print("E%i drawn" % (2*i+1))        
        
        # Draw optical IOs - North and South faces
        opio_north_xoffset = x0 - btu_recth/4 
        opio_north_yoffset = y0 
        opio_south_xoffset = x0 - btu_recth/4 
        opio_south_yoffset = y0 + N*ypitch + btu_recth
        for i in range(N):
            # North Edge
            key = "N%i" % (2*i)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(90)     
            opIOs[key].setPos(opio_north_xoffset+i*xpitch, opio_north_yoffset)
            if (_DEBUG): print("N%i drawn" % (2*i))
            key = "N%i" % (2*i+1)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(90)     
            opIOs[key].setPos(opio_north_xoffset+i*xpitch+btu_tot_len, opio_north_yoffset)
            if (_DEBUG): print("N%i drawn" % (2*i+1))
            #
            # South Edge
            key = "S%i" % (2*i)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(270)     
            opIOs[key].setPos(opio_south_xoffset+i*xpitch, opio_south_yoffset)
            if (_DEBUG): print("S%i drawn" % (2*i))
            key = "S%i" % (2*i+1)
            self.addItem(opIOs[key])
            opIOs[key].setRotation(270)     
            opIOs[key].setPos(opio_south_xoffset+i*xpitch+btu_tot_len, opio_south_yoffset)
            if (_DEBUG): print("S%i drawn" % (2*i+1))        
       
    
class ClickableItemView(QGraphicsView):
    def mousePressEvent(self, event):
        super(ClickableItemView, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsRectItem):
                print('item %s clicked!' % item.data(0))





