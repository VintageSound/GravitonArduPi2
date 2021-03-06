import asyncio
import gc
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
from dataAccess.pwmAccess import pwmAccess
from dataAccess.arduinoAccess import arduinoAccess
from dataAccess.cameraAccess import cameraAccess
from dataAccess.serverAccess import serverAccess
from dataAccess.pendulumSimulation import pendulumSimulation
import os

KD = 0.2
KI = 1E-9
KP = 0.01

class systemExperiment():
    def __init__(self, isSimulation = False, dataBufferSize = 100, sendToServer = True):
        self.polarity = 1
        
        self.dataAccess = None 
        self.serverAccess = serverAccess()
        
        self.fitLength = 15
        self.qCollectData = queue.LifoQueue()
        self.qPlot = queue.LifoQueue()
        self.qServerTransfer = queue.Queue()
        self.toTerminate = False
        self.dataBufferSize = dataBufferSize
        self.sendToServer = sendToServer
        self.integral = 0
        self.toPlotData = False
        self.learningRateKi = 1E-11
        self.learningRateKd = 0.001
        self.learningRateKp = 0.001
        self.errorIntegral = 0
        self.toAdjustPID = False
        
        if isSimulation:
            self.dataAccess = pendulumSimulation()
            self.pwmAccess = self.dataAccess
        else:
            self.switchToCamera()
            # self.switchToArduino()
            self.pwmAccess = pwmAccess()
        

    def switchToCamera(self):
        if self.dataAccess is not None: 
            self.dataAccess.close()
        
        self.dataSourceCamera = True
        self.dataAccess = cameraAccess()
        self.dataAccess.waitForInitialization()
        
        self.Kdeferential = 5 * self.polarity
        self.Kproportional = 0 * self.polarity
        self.Kintegral = 0 * self.polarity
        self.refreshRate = 1
        
        self.data = timeDataTuple([0],[0])
        self.control = timeDataTuple([0],[0])
        gc.collect()
        
    def switchToArduino(self):
        if self.dataAccess is not None: 
            self.dataAccess.close()
            time.sleep(2)
            
        self.dataSourceCamera = False
        self.dataAccess = arduinoAccess()
        self.dataAccess.waitForInitialization()
        
        self.Kdeferential = KD * self.polarity
        self.Kproportional = KP * self.polarity
        self.Kintegral = KI * self.polarity
        self.refreshRate = 5
        
        self.data = timeDataTuple([0],[0])
        self.control = timeDataTuple([0],[0])
        gc.collect()

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
                [data, control, fit] = self.qServerTransfer.get(timeout = 2)
                await self.serverAccess.sendDataToServer(data, control, fit)
            except Empty as ex:
                print("send to server queue is empty")
            except Exception as ex:
                print("Error in sending data to server: ", ex)
        
    def readData(self):
        return self.dataAccess.readData() 
    
    def setNewControlValue(self, value):
        self.pwmAccess.setNewControlValue(value)
        pass 

    def calculateNewControlValue(self, data):
        fit, prediction, predictionDerivaive  = self._makeFit(data, self.fitLength)
        self.integral += np.trapz(fit.data, fit.time) 

        derivativePower = -self.Kdeferential * predictionDerivaive.data[-1]
        # rootPower = self.Kroot * np.sqrt(np.abs(prediction.data[-1])) * -1 * np.sign(prediction.data[-1])
        proportionalPower = -self.Kproportional * prediction.data[-1]
        integralPower = -self.Kintegral * self.integral

        power = derivativePower + proportionalPower + integralPower
        controlValue = self._normalizeOutput(power)

        self.pwmAccess.setNewControlValue(controlValue)

        # print("lag: ", data.timeElapsedSinceUpdate()) 

        return timeDataTuple([fit.time[-1]], [controlValue]), fit

    def updatePIDbyGradientDescent(self, control, newData):
        if len(control.data) < 2 or control.data[-1] == control.data[-2]:
            return
        
        if newData.time[0] != control.time[-2]:
            raise Exception("time not mutched")

        dataControlDerivative = (newData.data[-1] - newData.data[0]) / (control.data[-1] - control.data[-2])
        newError = [d**2 for d in newData.data]
        e_t = newError[-1]
        d_e_t_dt = (newError[-1] - newError[-2]) / (newData.time[-1] - newData.time[-2])
        self.errorIntegral += np.trapz(newError, newData.time)

        self.Kproportional += self.learningRateKp * e_t * dataControlDerivative
        self.Kintegral += self.learningRateKi * e_t * dataControlDerivative * self.errorIntegral
        self.Kdeferential += self.learningRateKd * e_t * dataControlDerivative * d_e_t_dt
        
        if self.Kproportional < 0 : self.Kproportional = 0
        if self.Kintegral < 0 : self.Kintegral = 0 
        if self.Kdeferential < 0 : self.Kdeferential = 0  
        
        print("Kp: ", self.Kproportional, " Ki: ", self.Kintegral, " kd: ", self.Kdeferential)

        if np.isnan(self.Kproportional) or np.isnan(self.Kintegral) or np.isnan(self.Kdeferential):
            raise Exception("PID Parameter is NaN")
    
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
                self.data.extend(dataRecived)

                newControl, fit = self.calculateNewControlValue(self.data)
                newFit = fit.getDataAfter(self.control.time[-1])
                self.control.extend(newControl)
                
                if self.toAdjustPID:
                    self.updatePIDbyGradientDescent(self.control,newFit)

                self.data.clip(self.dataBufferSize)
                self.control.clip(self.dataBufferSize)
                
                if self.toPlotData and i % self.refreshRate == 0:
                    try:
                        # empty queue before inserting new data 
                        self.qPlot.get_nowait()
                    except:
                        pass

                    self.qPlot.put([self.data.copy(), self.control.copy(), fit])

                if self.sendToServer:
                    self.qServerTransfer.put([dataRecived.copy(), self.control.getDataAfter(lastRecivedTime), fit.getDataAfter(lastRecivedTime)])

                self.lastRecivedTime = self.data.time[-1]
                dataRecived.clear()

                i = i + 1
        except Exception as ex:
            print(ex)
            self.toTerminate = True
        finally:
            pass    

    def listenToInput(self):
        print("Listening to input")

        while not self.toTerminate:
            try:
                inputChar = input()

                if inputChar == 'l' :
                    if not self.toAdjustPID:
                        self.toAdjustPID = True
                        self.errorIntegral = 0 
                        print("Adjust PID parameters on")
                    else:
                        self.toAdjustPID = False
                        print("Adjust PID parameters off")
                elif inputChar == 'c':
                    if not self.dataSourceCamera:
                        self.switchToCamera()
                    else:
                        self.switchToArduino()
                elif inputChar == 'e':
                    self.toTerminate = True
                else:
                    print("command not recognized")
            except Exception as ex:
                print(ex)
                self.toTerminate = True
                

    def plotData(self):
        self.toPlotData = True
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

    def startProcesses(self, toProcessDataThread, toPlotDataThread):
        self.toProcessDataThread = toProcessDataThread
        self.toPlotDataThread = toPlotDataThread

        self.collectDataProcess = threading.Thread(target=self.collectData)
        self.sendToServerProcess = threading.Thread(target=self.sendDataToServer)
        self.plotProcess = threading.Thread(target=self.plotData)
        self.processDataProcess = threading.Thread(target=self.processData)
        self.listenToInputProcess = threading.Thread(target=self.listenToInput)
        
        self.collectDataProcess.start()
        self.listenToInputProcess.start()

        if self.sendToServer:
            self.sendToServerProcess.start()

        if self.toPlotDataThread:
            self.plotProcess.start()

        if self.toProcessDataThread:
            self.processDataProcess.start()

    def terminateProcesses(self):
        self.toTerminate = True
        self.collectDataProcess.join(2)
        
        if self.toProcessDataThread:
            self.processDataProcess.join(2)

        if self.toPlotDataThread:
            self.plotProcess.join(2)
            
        self.setNewControlValue(0)

        if self.sendToServer:
            self.sendToServerProcess.join(2)
            
            if self.sendToServerProcess.is_alive():
                print("send to server process did not ended properly")

        self.closeConnection()
        
        self.listenToInputProcess.join(2)