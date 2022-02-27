
from bussinessLogic.systemExperiment import systemExperiment
from bussinessLogic.systemSimulation import systemSimulation

sendToServerThread = False 
toPlotDataThread = False
proccesDataThread = True
toSimulate = True
pointsToShow = 100

system = systemExperiment(pointsToShow, proccesDataThread, sendToServer, toPlotData, toSimulate)
system.startProcesses()

try:
    system.processData()
except KeyboardInterrupt:
    print("exiting")
except Exception as ex:
    print(ex)
    raise ex
finally:
    system.terminateProcesses()
