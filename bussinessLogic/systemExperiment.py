import asyncio
import time
from numpy.lib.ufunclike import _fix_out_named_y
from utilities.plotter import plotter 
from dataStructures.timeDataTuple import timeDataTuple
import numpy as np
import ctypes
import queue
import threading

from queue import Empty
from numpy import sign
from dataStructures.timeDataTuple import timeDataTuple
# from dataAccess.pwmAccess import pwmAccess
# from dataAccess.arduinoAccess import arduinoAccess
from dataAccess.serverAccess import serverAccess
from dataAccess.pendulumSimulation import pendulumSimulation
import os

class systemExperiment():
    def __init__(self, dataBufferSize, sendToServer, toPlotData, isSimulation):
        # os.system("sudo pigpiod")
        if isSimulation:
            self.dataAccess = pendulumSimulation()
            self.pwmAccess = self.dataAccess
        else:
            self.dataAccess = arduinoAccess()
            self.pwmAccess = pwmAccess()
        
        self.serverAccess = serverAccess()
        self.newControl = []
        
        polarity = 1
        self.Kdeferential = 0.1 * polarity
        self.Kroot = 0 * polarity
        self.Kproportional = 0.005 * polarity
        self.fitLength = 20
        self.qCollectData = queue.LifoQueue()
        self.qPlot = queue.LifoQueue()
        self.qServerTransfer = queue.Queue()
        self.toTerminate = False
        self.dataBufferSize = dataBufferSize
        self.sendToServer = sendToServer
        self.toPlotData = toPlotData
        
    def waitForInitalization(self):   
        self.dataAccess.waitForInitialization()

    def increaseEfficiency(self):   
        processid = os.getpid()
        os.system("sudo renice -n -19 -p " + str(processid))
    
    def sendDataToServer(self):
        asyncio.run(self._sendDataToServer())

    async def _sendDataToServer(self):
        while not self.toTerminate:
            try:
                [data, control, fit] = queue.get(timeout = 1)
                await self.serverAccess.sendDataToServer(data, control, fit)
            except Empty as ex:
                print("send to server queue is empty")
            except Exception as ex:
                print("Error in sending data to server: ", ex)
        
    def readData(self):
        return self.dataAccess.readData(0) 
    
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
        self.dataAccess.close()
        pass

    def _makeFit(self, data, fitLength):    
        if len(data.time) < fitLength:
            #TODO: Change to correct derivative
            return data.copy(), data.copy(), data.copy()
        
        fit = np.polyfit(data.time[-fitLength:], data.data[-fitLength:],3)
        t_fit = data.time[-fitLength:]
        x_fit = [self._getDataForFitPoly3(fit, _t) for _t in t_fit]
        
        fitData = timeDataTuple(t_fit,x_fit)
    
        timeNextStep = t_fit[-1] + data.timeElapsedSinceUpdate() * 1.1
        dataNextStep = self._getDataForFitPoly3(fit, timeNextStep)
        derivativeNextStep = self._getDerivativeForFitPoly3(fit, timeNextStep) 
        prediction = timeDataTuple([timeNextStep], [dataNextStep])
        predictionDerivaive = timeDataTuple([timeNextStep], [derivativeNextStep])

        return fitData, prediction, predictionDerivaive

    def _getDataForFitPoly3(self, fit, _t):
        return fit[0] * _t**3 + fit[1] * _t**2 + fit[2] * _t + fit[3]

    def _getDerivativeForFitPoly3(self, fit, _t):
            return fit[0] * 3 * _t**2 + fit[1] * 2* _t + fit[2]

    def _normalizeOutput(self, pidOutput):    
        normalization = 50
        
        norm = pidOutput * normalization
        
        if abs(norm) > 1:
            return np.sign(norm)
        
        return norm

    def collectData(self):
        while not self.toTerminate:
            try:
                newData = self.readData()
                
                if newData is None or len(newData.data) == 0:
                    continue
    
                self.qCollectData.put(newData)    
            except Exception as ex:
                print("Error while collecting data: ", ex)
    
    def processData(self):
        
        #TODO: check if needed
        # self.increaseEfficiency()

        data = timeDataTuple([0],[0])
        control = timeDataTuple([0],[0])
        dataRecived = timeDataTuple([],[])
        lastRecivedTime = 0

        i = 1

        try:
            while not self.toTerminate:
                for n in range(5):
                    if self.qCollectData.empty():
                        break
                    
                    newData = self.qCollectData.get()
                    if newData.time[0] > lastRecivedTime:
                        dataRecived.extend(newData)
                    
                if len(dataRecived.data) == 0:
                    continue

                dataRecived.sortByTime()
                data.extend(dataRecived)

                newControl, fit = self.calculateNewControlValue(data)

                control.extend(newControl)
                
                data.clip(self.dataBufferSize)
                control.clip(self.dataBufferSize)
                
                if self.toPlotData and i % 5 == 0:
                    self.qPlot.put([data.copy(), control.copy(), fit])

                if self.sendToServer:
                    self.qServerTransfer.put([dataRecived.copy(), control.getDataAfter(lastRecivedTime), fit.getDataAfter(lastRecivedTime)])

                lastRecivedTime = data.time[-1]
                dataRecived.clear()

                i = i + 1
        except Exception as ex:
            print(ex)
            self.toTerminate = True
        finally:
            pass    

    def plotData(self):
        plot = plotter(self.dataBufferSize)
        lastRecivedTime = 0

        while plot.isFigureOpen() and not self.toTerminate:
            try:
                [data, control, fit] = self.qPlot.get()
                
                if np.any(data.data) and data.time[-1] > lastRecivedTime:
                    plot.drawLine('control',control.time,control.data,'r-', fitBoundriesToX = False, fitBoundriesToY = True)
                    plot.drawLine('x',data.time, data.data,'b.', fitBoundriesToX = True, fitBoundriesToY = True)
                    plot.drawLine('fit',fit.time,fit.data,'tab:orange', fitBoundriesToX = False, fitBoundriesToY = False)
                    plot.refresh()

                    lastRecivedTime = data.time[-1]
            except Exception as ex:
                print(ex)

        self.toTerminate = True

    def startProcesses(self):
        self.waitForInitalization()

        self.collectDataProcess = threading.Thread(target=self.collectData)
        self.sendToServerProcess = threading.Thread(target=self.sendDataToServer)
        self.plotProcess = threading.Thread(target=self.plotData)

        self.collectDataProcess.start()

        if self.sendToServer:
            self.sendToServerProcess.start()

        if self.toPlotData:
            self.plotProcess.start()

    def terminateProcesses(self):
        self.toTerminate = True
        self.collectDataProcess.join(2)
        
        if self.toPlotData:
            self.plotProcess.join(2)
            
        self.setNewControlValue(0)

        if self.sendToServer:
            self.sendToServerProcess.join(2)
            
            if self.sendToServerProcess.isAlive():
                print("send to server process did not ended properly")

        self.closeConnection()