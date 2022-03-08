
from bussinessLogic.systemExperiment import systemExperiment

sendToServerThread = False 
toPlotDataThread = False
processDataThread = True
toSimulate = False
pointsToShow = 100

system = systemExperiment(toSimulate, pointsToShow, sendToServerThread)
system.startProcesses(processDataThread, toPlotDataThread)

try:
    system.plotData()
except KeyboardInterrupt:
    print("exiting")
except Exception as ex:
    print(ex)
    raise ex
finally:
    system.terminateProcesses()
