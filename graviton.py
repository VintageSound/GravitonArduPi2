
from numpy.lib.ufunclike import _fix_out_named_y
from bussinessLogic.systemExperiment import systemExperiment
from bussinessLogic.systemSimulation import systemSimulation
from utilities.plotter import plotter 
from dataStructures.timeDataTuple import timeDataTuple
import numpy as np
import multiprocessing as mp
import ctypes
import queue
import threading

system = systemExperiment()

def collectData(qCollectData, qCollectErrors, toTerminate):
    while not bool(toTerminate.value):
        try:
            newData = system.readData()
            
            if len(newData.data) == 0:
                qCollectErrors.put(newData)
                continue
   
            qCollectData.put(newData)    
        except Exception as ex:
            qCollectErrors.put(ex)

def plotData(qPlot, pointsToShow, toTerminate):
    plot = plotter(pointsToShow)
    lastRecivedTime = 0

    while plot.isFigureOpen() and not bool(toTerminate.value):
        try:
            [data, control, fit] = qPlot.get()
            
            if np.any(data.data) and data.time[-1] > lastRecivedTime:
                plot.drawLine('control',control.time,control.data,'r-', fitBoundriesToX = False, fitBoundriesToY = True)
                plot.drawLine('x',data.time, data.data,'b.', fitBoundriesToX = True, fitBoundriesToY = True)
                plot.drawLine('fit',fit.time,fit.data,'tab:orange', fitBoundriesToX = False, fitBoundriesToY = False)
                plot.refresh()

                lastRecivedTime = data.time[-1]
        except Exception as ex:
            print(ex)

    toTerminate.Value = True

def processData(qPlot, qCollectData, qServerTransfer, toTerminate, pointsToShow):
    system.increaseEfficiency()

    data = timeDataTuple([0],[0])
    control = timeDataTuple([0],[0])
    dataRecived = timeDataTuple()
    lastRecivedTime = 0

    i = 1

    try:
        while not bool(toTerminate.value):
            for n in range(5):
                if qCollectData.empty():
                    break
                
                newData = qCollectData.get()
                if newData.time[0] > lastRecivedTime:
                    dataRecived.extend(newData)
                else:
                    qServerTransfer.put([newData, timeDataTuple(), timeDataTuple()])

            if len(dataRecived.data) == 0:
                continue

            dataRecived.sortByTime()
            data.extend(dataRecived)

            newControl, fit = system.calculateNewControlValue(data)

            control.extend(newControl)
            
            data.clip(pointsToShow)
            control.clip(pointsToShow)
            
            if i % 5 == 0:
                qPlot.put([data.copy(), control.copy(), fit])

            qServerTransfer.put([dataRecived, control.getDataAfter(lastRecivedTime), fit.getDataAfter(lastRecivedTime)])

            lastRecivedTime = data.time[-1]
            dataRecived.clear()

            i = i + 1
    except Exception as ex:
        print(ex)
        toTerminate.value = True
    finally:
        pass    

def sendToServer(qServerTransfer, toTerminate):
    while not bool(toTerminate.value):
        [data, control, fit] = qServerTransfer.get()
        system.sendDataToServer(data, control, fit)

pointsToShow = 100

# run simulation instead of real data
# system = systemSimulation()

system.waitForInitalization()

qCollectData = queue.LifoQueue()
qCollectErrors = queue.LifoQueue()
qPlot = queue.LifoQueue()
qServerTransfer = queue.Queue()
toTerminate = mp.Value(ctypes.c_bool, False)

collectDataProcess = threading.Thread(target=collectData, args=(qCollectData, qCollectErrors, toTerminate, ))
processDataProcess = threading.Thread(target=processData, args=(qPlot, qCollectData, qServerTransfer, toTerminate, pointsToShow, ))
sendToServerProcess = threading.Thread(target=sendToServer, args=(qServerTransfer, toTerminate, ))
# sendToPCProcess =  
# plotProcess = mp.Process(target=plotData, args=(qPlot,pointsToShow, toTerminate, ))

# ygfh
collectDataProcess.start()
processDataProcess.start()
sendToServerProcess.start()
# plotProcess.start()



try:
    # processData(qPlot, qCollectXT, qPCTransfer, toTerminate, pointsToShow)
    plotData(qPlot, pointsToShow, toTerminate)
except KeyboardInterrupt:
    print("exiting")
except Exception as ex:
    print(ex)
    raise ex
finally:
    toTerminate.value = True
    collectDataProcess.join()    
    processDataProcess.join()
    system.setNewControlValue(0)
    system.closeConnection()
