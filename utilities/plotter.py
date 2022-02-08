# type this in the console
# %matplotlib qt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

class plotter:
    def __init__(self, pointsToShow = 10000):        
        plt.ion()    
        self.fig = plt.figure()
        self.figIndex = self.fig.number
        self.ax = self.fig.add_subplot(111)
        self.lines = {}    
        self.lineYBoundry = {}
        self.pointsToShow = pointsToShow
        # plt.ylim([-1.1,1.1])

    def isFigureOpen(self):
        return plt.fignum_exists(self.figIndex)
    
    def drawLine(self, lineName, x, y, lineStyle = 'r-', fitBoundriesToX = True, fitBoundriesToY = True):
        if lineName in self.lines:
            self.lines[lineName].set_data(x,y)
            
            if fitBoundriesToX:
                self.chagneFigureBoundriesX(x, lineName)
            
            if fitBoundriesToY:
                self.chagneFigureBoundriesY(y, lineName)
        else:
            newLine, = self.ax.plot(x, y, lineStyle)
            self.lines[lineName] = newLine
            plt.show()
            # line2, = ax.plot(x, a1, 'b-')
            
    
    def getBoundry(self, y, startIndex):
        minVal = np.min(y[startIndex:])
        maxVal = np.max(y[startIndex:])
        
        if abs(minVal) > abs(maxVal):
            boundry = abs(minVal)
        else:
            boundry = abs(maxVal)
        
        return boundry
    
    def chagneFigureBoundriesX(self, x, lineName):
        startIndex = self.getStartIndex(x)
        xEnd = x[-1]
         
        xStart = x[startIndex]
        
        plt.xlim([xStart,xEnd])
    
    def chagneFigureBoundriesY(self, y, lineName):
        startIndex = self.getStartIndex(y)
        
        boundry = self.getBoundry(y, startIndex)
        
        self.lineYBoundry[lineName] = boundry
        
        for b in self.lineYBoundry.values():
            if b > boundry:
                boundry = b
        
        if (boundry > 0):
            plt.ylim([-boundry*1.1,boundry*1.1])
    

    def refresh(self):
        plt.pause(0.01)
        
    def getStartIndex(self, x):
        startIndex = 0
        if len(x) > self.pointsToShow:
            startIndex = len(x) - 1 - self.pointsToShow

        return startIndex

        