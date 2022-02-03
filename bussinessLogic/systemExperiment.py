import asyncio
from numpy import sign
from dataStructures.timeDataTuple import timeDataTuple
from dataAccess.pwmAccess import *
from dataAccess.arduinoAccess import *
from dataAccess.serverAccess import serverAccess
import os

class systemExperiment():
    def __init__(self):
        # os.system("sudo pigpiod")
        self.arduinoAccess = arduinoAccess()
        self.pwmAccess = pwmAccess()
        self.serverAccess = serverAccess()
        self.newControl = []
        
        polarity = 1
        self.Kdeferential = 0.5 * polarity
        self.Kroot = 0.001 * polarity
        self.Kproportional = 0 * polarity
        self.fitLength = 20
        
    def waitForInitalization(self):   
        self.arduinoAccess.waitForInitialization()
        pass

    def increaseEfficiency(self):   
        processid = os.getpid()
        os.system("sudo renice -n -19 -p " + str(processid))
    
    def sendDataToServer(self, queue, toTerminate):
        asyncio.run(self._sendDataToServer(queue, toTerminate))

    def stopSendingToServer(self):
        asyncio.gather() 

    async def _sendDataToServer(self, queue, toTerminate):
        while not bool(toTerminate.value):
            [data, control, fit] = queue.get()
            await self.serverAccess.sendDataToServer(data, control, fit)
        
    def readData(self):
        return self.arduinoAccess.readData(0) 
    
    def setNewControlValue(self, value):
        self.pwmAccess.setNewControlValue(value)

    def calculateNewControlValue(self, data):
        fit, fitDervative = self._makeFit(data, self.fitLength)
        derivativePower = self.Kdeferential * fitDervative.data[-1]
        rootPower = self.Kroot * np.sqrt(np.abs(fit.data[-1])) * -1 * np.sign(fit.data[-1])
        proportionalPower = -1 * self.Kproportional * fit.data[-1]

        power = derivativePower + rootPower + proportionalPower
        controlValue = self._normalizeOutput(power)

        self.pwmAccess.setNewControlValue(controlValue)

        return timeDataTuple([fit.time[-1]], [controlValue]), fit

    def closeConnection(self):
        self.arduinoAccess.close()
        pass

    def _makeFit(self, data, fitLength):    
        if len(data.time) < fitLength:
            #TODO: Change to correct derivative
            return data.copy(), data.copy()
        
        fit = np.polyfit(data.time[-fitLength:], data.data[-fitLength:],3)
        t_fit = data.time[-fitLength:]
        x_fit = [fit[0] * _t**3 + fit[1] * _t**2 + fit[2] * _t + fit[3] for _t in t_fit]
        derivative_fit = [fit[0] * 3 * _t**2 + fit[1] * 2* _t + fit[2] for _t in t_fit]

        fitData = timeDataTuple(t_fit,x_fit)
        fitDerivative = timeDataTuple(t_fit,derivative_fit)
        return fitData, fitDerivative 

    def _normalizeOutput(self, pidOutput):    
        normalization = 50
        
        norm = pidOutput * normalization
        
        if abs(norm) > 1:
            return np.sign(norm)
        
        return norm

    