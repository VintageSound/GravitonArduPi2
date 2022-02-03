import gc

class timeDataTuple():
    def __init__(self, time = [], data = []):
        self.time = time
        self.data = data

    def extend(self, timeData):
        self.time.extend(timeData.time)
        self.data.extend(timeData.data)

    def sortByTime(self):
        self.data = [x for t,x in sorted(zip(self.time,self.data))]
        self.time.sort()

    def clear(self):
        self.data.clear()
        self.time.clear()

    def copy(self):
        return timeDataTuple(self.time.copy(), self.data.copy())

    def clip(self, pointsToSave):
        if len(self.time) < pointsToSave:
            return

        self.time = self.time[-pointsToSave:]
        self.data = self.data[-pointsToSave:]
        
        gc.collect()

    def getDataAfter(self, time):
        filteredTime = [self.time[i] for i in range(len(self.time)) if self.time[i] >= time]
        filteredData = [self.data[i] for i in range(len(self.time)) if self.time[i] >= time]

        return timeDataTuple(filteredTime, filteredData)


## example
# ex = timeDataTuple([4,3,2,1], ['1', '2' , '3', '4'])
# print(ex.time, ex.data)

# ex.sortByTime()
# print(ex.time, ex.data)