# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 10:22:17 2021

@author: USER
"""

from arduinoSimulation import *
from arduinoManager import *
from utiliplotter import *
from pidController import *
import numpy as np
import time
from geneticalgorithm import geneticalgorithm as ga


def fitness(variables):
    arduino.waitForInitalization()
    
    x = pidController.runOparetion(variables[0], variables[1], variables[2])
    
    return -np.average(x)


P = 0.05
I = 0
D = 0.00005

# arduino = arduinoManager()

# run simulation instead of real arduino
arduino = arduinoSimulation()
pidController = pidController() 


varbound=np.array([[0,10]]*3)

model=ga(function=fitness,dimension=3,variable_type='real',variable_boundaries=varbound)

model.run()



plot = plotter(1000)

t = []
x = []
y = []
sums = []
control = []

# assume we have a system we want to control in controlled_system
# v = controlled_system.update(0)

i = 0

try:
            
except KeyboardInterrupt:
    print("exiting")
finally:    
    arduino.closeConnection()
 