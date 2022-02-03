from utilities.plotter import plotter
from server.bussinessLogic.serverLogic import serverLogic
import numpy as np

server = serverLogic()
server.startListenToClient()

def plotData(pointsToShow):
    plot = plotter(pointsToShow)
    lastRecivedTime = 0

    while plot.isFigureOpen() and not server.toTerminate:
        try:
            server.proccessNewData()
            
            if len(server.data.time) == 0:
                continue

            plot.drawLine('control',server.control.time, server.control.data,'r-', fitBoundriesToX = False, fitBoundriesToY = True)
            plot.drawLine('x',server.data.time, server.data.data,'b.', fitBoundriesToX = True, fitBoundriesToY = True)
            plot.drawLine('fit',server.fit.time, server.fit.data,'tab:orange', fitBoundriesToX = False, fitBoundriesToY = False)
            plot.refresh()

        except Exception as ex:
            print(ex)

try:
    # processData(qPlot, qCollectXT, qPCTransfer, toTerminate, pointsToShow)
    plotData(1000)
except KeyboardInterrupt:
    print("exiting")
except Exception as ex:
    print(ex)
    raise ex
finally:
    server.stopListenToClient()
