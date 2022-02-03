# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 21:11:05 2021

@author: USER
"""

from arduinoSimulation import *
from arduinoManager import *
from plotter import *
from simple_pid import PID
import numpy as np
import time

class pidController():
    def __init__(self):
        pass
        
    def normalizeOutput(pidOutput):    
        if abs(pidOutput) > 1:
            return np.sign(pidOutput)
        
        return value
        
    def runOparetion(self, p, i, d, norm, oparetionTime, plotter, arduino)    
        t = []
        x = []
        y = []
        sums = []
        control = []
        startTime = time.perf_counter()        
        
        pid = PID(p, i, d, setpoint=0)
    
        i = 0
        
        while plot.isFigureOpen() and time.perf_counter() - startTime < oparetionTime:
            timeNew, xNew, yNew, sumNew = arduino.readData()
            t.extend(timeNew)
            x.extend(xNew)
            y.extend(yNew)
            # who cares about sum
            # sums.extend(sumNew)
            
            # Add each element to the pid to get the right diff and int
            for element in xNew:
                control.append(normalizeOutput(pid(element)))
            
            arduino.setNewControlValue(control[-1])
        
            if i % 2 == 0:
                 plotter.drawLine('x',t,x,'b-')
                 plotter.drawLine('control',t,control,'r-')
                 plotter.refresh()
                
            i = i + 1
            
        return x
                
         