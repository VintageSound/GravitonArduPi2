import asyncio
from queue import Empty
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
        self.Kdeferential = 0.1 * polarity
        self.Kroot = 0 * polarity
        self.Kproportional = 0.005 * polarity
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
        # asyncio.gather() 
        pass

    async def _sendDataToServer(self, queue, toTerminate):
        while not bool(toTerminate.value):
            try:
                [data, control, fit] = queue.get(timeout = 1)
                await self.serverAccess.sendDataToServer(data, control, fit)
            except Empty as ex:
                print("send to server queue is empty")
            except Exception as ex:
                print("Error in sending data to server: ", ex)
        
    def readData(self):
        return self.arduinoAccess.readData(0) 
    
    def setNewControlValue(self, value):
        self.pwmAccess.setNewControlValue(value)

    def calculateNewControlValue(self, data):
        fit, prediction, predictionDerivaive  = self._makeFit(data, self.fitLength)
        derivativePower = -self.Kdeferential * predictionDerivaive.data[-1]
        rootPower = self.Kroot * np.sqrt(np.abs(prediction.data[-1])) * -1 * np.sign(prediction.data[-1])
        proportionalPower = -1 * self.Kproportional * prediction.data[-1]

        power = derivativePower + rootPower + proportionalPower
        controlValue = self._normalizeOutput(power)

        self.pwmAccess.setNewControlValue(controlValue)

        print("lag: ", data.timeElapsedSinceUpdate()) 

        return timeDataTuple([fit.time[-1]], [controlValue]), fit

    def closeConnection(self):
        self.arduinoAccess.close()
        pass

    def _makeFit(self, data, fitLength):    
        if len(data.time) < fitLength:
            #TODO: Change to correct derivative
            return data.copy(), data.copy(), data.copy()
        
        fit = np.polyfit(data.time[-fitLength:], data.data[-fitLength:],3)
        t_fit = data.time[-fitLength:]
        x_fit = [self.getDataForFitPoly3(fit, _t) for _t in t_fit]
        
        fitData = timeDataTuple(t_fit,x_fit)
    
        timeNextStep = t_fit[-1] + data.timeElapsedSinceUpdate() * 1.1
        dataNextStep = self.getDataForFitPoly3(fit, timeNextStep)
        derivativeNextStep = self.getDerivativeForFitPoly3(fit, timeNextStep) 
        prediction = timeDataTuple([timeNextStep], [dataNextStep])
        predictionDerivaive = timeDataTuple([timeNextStep], [derivativeNextStep])

        return fitData, prediction, predictionDerivaive

    def getDataForFitPoly3(self, fit, _t):
        return fit[0] * _t**3 + fit[1] * _t**2 + fit[2] * _t + fit[3]

    def getDerivativeForFitPoly3(self, fit, _t):
            return fit[0] * 3 * _t**2 + fit[1] * 2* _t + fit[2]

    def _normalizeOutput(self, pidOutput):    
        normalization = 50
        
        norm = pidOutput * normalization
        
        if abs(norm) > 1:
            return np.sign(norm)
        
        return norm