from dataStructures.timeDataTuple import timeDataTuple
from server.dataAccess.clientListener import clientListener
import asyncio
import queue
import threading
import pandas as pd
from datetime import datetime

class serverLogic:
    def __init__(self):
        self.qData = queue.Queue()
        self.data = timeDataTuple([],[])
        self.control = timeDataTuple([],[])
        self.fit = timeDataTuple([],[])
        self.dataLock = threading.Lock()
        self.toTerminate = False

    def startListenToClient(self):
        self.createNewCsvFile()
        self.index = 0
        self.listeningProccess = threading.Thread(target=self.listen)
        self.listeningProccess.start()

    def createNewCsvFile(self):
        self.dataFileName = "Data\\Graviton_data_" + datetime.now().strftime("%d_%m,%H_%M") + ".csv"
        self.controlFileName = "Data\\Graviton_control_" + datetime.now().strftime("%d_%m,%H_%M") + ".csv"
                
    def stopListenToClient(self):
        self.toTerminate = True
        asyncio.gather()
        self.listeningProccess.join()
        self.saveData()

    def saveData(self):
        dataDict = {'time': self.data.time, 'data' : self.data.data}
        controlDict = {'control time' : self.control.time, 'control data' : self.control.data}
        dfData = pd.DataFrame(dataDict)
        dfControl = pd.DataFrame(controlDict)
        dfData.to_csv(self.dataFileName, mode='a')
        dfControl.to_csv(self.controlFileName, mode='a')

        print("Data saved")

    def proccessNewData(self):
        for n in range(5):
            if self.qData.empty():
                break
            
            [newData, newControl, newFit] = self.qData.get()
            if len(newControl.time) > 0:
                self.control.extend(newControl)
                
            if len(newFit.time) > 0:
                self.fit.extend(newFit)
                
            if len(newData.time) > 0:
                self.data.extend(newData)
        
        if (len(self.data.time) != 0):
            self.data.sortByTime()
            self.control.sortByTime()
            self.fit.sortByTime()

        if len(self.data.time) > 1000:
            self.saveData()
            self.data.clear()
            self.control.clear()
            self.fit.clear()
        
    def listen(self):
        asyncio.run(self._listen())

    async def _listen(self):
        listener = clientListener()
        await listener.initSocket()

        try:
            while not self.toTerminate:
                newData, newControl, newFit = await listener.waitForDataFromClient()
                # debug
                newData = newData.copy()
                newControl = newControl.copy()
                newFit = newFit.copy()

                newData.checkIfTupleValid()
                newControl.checkIfTupleValid()
                newFit.checkIfTupleValid()
                self.qData.put([newData, newControl, newFit])
        except Exception as ex:
            print(ex)

