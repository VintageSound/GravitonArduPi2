from dataAccess.pendulumSimulation import *
from time import sleep

class systemSimulation():
    def __init__(self):
        print ('simulation begins')
        
#    def __del__(self):            
#        self.serialStream.close()

    # do nothing
    def waitForInitalization(self):   
        self.simulation = pendulumSimulation()
        
    def increaseEfficiency(self):
        pass

    def readData(self):
        # for now only returns x
        t, x = self.simulation.getNextStep()
        sleep(self.simulation.stepTime)
        # y = []
        # summ  = []
        
        return t, x
    
    def setNewControlValue(self, controlValue):
        self.simulation.setNewControlValue(controlValue * 1000)
        
    # do nothing
    def closeConnection(self):
        pass
        