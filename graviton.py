
from bussinessLogic.systemExperiment import systemExperiment

sendToServerThread = True 
toPlotDataThread = False
processDataThread = False
toSimulate = False
pointsToShow = 100

system = systemExperiment(toSimulate, pointsToShow, sendToServerThread)
system.startProcesses(processDataThread, toPlotDataThread)

try:
    system.processData()
    # system.plotData()
except KeyboardInterrupt:
    print("exiting")
except Exception as ex:
    print(ex)
    raise ex
finally:
    system.terminateProcesses()

