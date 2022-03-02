import numpy as np
import math
from scipy.integrate import odeint
import time
from dataStructures.timeDataTuple import timeDataTuple

class pendulumSimulation:
    def __init__(self):        
        # pendulum parameters
        m=.2
        r=0.5
        self.I=2*m*r**2

        self.period = 200 #The period of the pendulum
        self.omega = 2 * math.pi / self.period  # The angular frequency of the pendulum
        self.damping = 0.1 # damping dimentionless parameter
        self.x =  [0.1] # [np.random.uniform(0,2)]
        self.dx_dt = [0] # [np.random.uniform(0,2)]
        self.t = 0
        self.time = []
        self.stepTime = 0.1
        self.steps = 100
        self.control = 0
        self.centerOffset = 0.1
        self.thermalNoiseStandartDeviation = 1E-6
    
    #This function is the second order diffential equation with forcing term
    def odePendulum(self, u, x):
        thermalNoise = np.random.normal(loc=0, scale=self.thermalNoiseStandartDeviation)
        # print(thermalNoise)
        return u[1], self.control/self.I - 2 * self.damping * self.omega * u[1] - (u[0] - self.centerOffset) * (self.omega ** 2) + thermalNoise
    
    def waitForInitialization(self):
        pass

    def readData(self, channelNumber = 0):
        t, x = self.getNextStep()
        return timeDataTuple([t], [x])

    def getNextStep(self):
        timeArrayForStep = np.linspace(self.t, self.t + self.stepTime, self.steps)
        time.sleep(0.001)
        currentPosition = [self.x[-1],self.dx_dt[-1]]
        
        Us = odeint(self.odePendulum, currentPosition, timeArrayForStep)
        
        self.time.extend(timeArrayForStep)
        self.x.extend(Us[:,0])
        self.dx_dt.extend(Us[:,1])
        
        self.t = self.t + self.stepTime
        
        return self.time[-1], self.x[-1]
    
    def setNewControlValue(self, newControl):
        self.control = newControl * 0.01
        pass
    
    def close(self):
        pass
