from dataStructures.timeDataTuple import timeDataTuple
from server.dataAccess.clientListener import clientListener
import asyncio
import queue
import threading

class serverLogic:
    def __init__(self):
        self.qData = queue.queue()
        self.data = timeDataTuple()
        self.control = timeDataTuple()
        self.fit = timeDataTuple()
        self.toTerminate = False
        self.listeningProccess = threading.Thread(target=self.listen)
        self.lastRecivedTime = 0

def startListenToClient(self):
    self.listeningProccess.start()

def stopListenToClient(self):
    self.toTerminate = True
    asyncio.gather()
    self.listeningProccess.join()

def proccessNewData(self):
    for n in range(5):
        if self.qData.empty():
            break
        
        [newData, newControl, newFit] = self.qData.get()
        if len(newControl) > 0:
            self.control.extend(newControl)
            
        if len(newFit) > 0:
            self.fit.extend(newFit)
            
        if len(newData) > 0:
            self.data.extend(newData)
            
    self.data.sortByTime()
    self.control.sortByTime()
    self.fit.sortByTime()

def listen(self):
    asyncio.run(listen())

async def _listen(self):
    listener = clientListener()
    await listener.initSocket()

    try:
        while not self.toTerminate:
            data, control, fit = await listener.waitForDataFromClient()
            self.qData.put([data, control, fit])
    except Exception as ex:
        print(ex)

