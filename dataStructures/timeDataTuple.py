import gc
from datetime import datetime
import time as t

class timeDataTuple():
    def __init__(self, time = [], data = []):
        self.updateTime = t.time()
        self.time = time
        self.data = data
        self.checkIfTupleValid()

    def extend(self, timeData):
        self.updateTime = timeData.updateTime
        self.time.extend(timeData.time)
        self.data.extend(timeData.data)

    def sortByTime(self):
        self.data = [x for t,x in sorted(zip(self.time,self.data))]
        self.time.sort()

    def clear(self):
        self.data.clear()
        self.time.clear()

    def copy(self):
        newTuple = timeDataTuple(self.time.copy(), self.data.copy())
        newTuple.updateTime = self.updateTime
        return newTuple

    def clip(self, pointsToSave):
        if len(self.time) < pointsToSave:
            return

        self.time = self.time[-pointsToSave:]
        self.data = self.data[-pointsToSave:]
        
        self.checkIfTupleValid()

        gc.collect()

    def getDataAfter(self, time):
        filteredTime = [self.time[i] for i in range(len(self.time)) if self.time[i] >= time]
        filteredData = [self.data[i] for i in range(len(self.time)) if self.time[i] >= time]

        if (len(filteredTime) != len (filteredData)):
            raise Exception("bug") 

        newTuple = timeDataTuple(filteredTime, filteredData)
        return newTuple

    def checkIfTupleValid(self):
        if len(self.time) != len(self.data):
            raise Exception("invalid tuple")
    
    def timeElapsedSinceUpdate(self):
        return t.time() - self.updateTime
## example
# ex = timeDataTuple([4,3,2,1], ['1', '2' , '3', '4'])
# print(ex.time, ex.data)

# ex.sortByTime()
# print(ex.time, ex.data)