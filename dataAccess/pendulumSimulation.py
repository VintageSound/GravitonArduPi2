
import numpy as np
import math
from scipy.integrate import odeint
import time

class pendulumSimulation:
    def __init__(self):        
        # pendulum parameters
        m=.2
        r=2
        self.I=3*m*r**2

        self.period = 1 #The period of the pendulum
        self.omega = 2 * math.pi / self.period  # The angular frequency of the pendulum
        self.damping = 0.5 # damping dimentionless parameter
        self.x =  [1] # [np.random.uniform(0,2)]
        self.dx_dt = [0] # [np.random.uniform(0,2)]
        self.t = 0
        self.time = []
        self.stepTime = 0.0001
        self.control = 0
    
    #This function is the second order diffential equation with forcing term
    def odePendulum(self, u,x):
        return u[1], self.control/self.I - 2 * self.damping * self.omega * u[1] - u[0] * (self.omega ** 2) 
    
    def getNextStep(self):
        timeArrayForStep = np.linspace(self.t, self.t + self.stepTime, 10)
        currentPosition = [self.x[-1],self.dx_dt[-1]]
        
        Us = odeint(self.odePendulum, currentPosition, timeArrayForStep)
        
        self.time.extend(timeArrayForStep)
        self.x.extend(Us[:,0])
        self.dx_dt.extend(Us[:,1])
        
        self.t = self.t + self.stepTime
        
        return self.time[-1], self.x[-1]
    
    def setNewControlValue(self, newControl):
        self.control = newControl
    
