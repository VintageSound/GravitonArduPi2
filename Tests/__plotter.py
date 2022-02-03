# type this in the console
# %matplotlib qt

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
# from pyqtgraph.Qt import QtGui, QtCore
# import pyqtgraph as pg

class plotter:
    def __init__(self, pointsToShow = 10000):        
#        plt.ion()    
        self.fig = plt.figure()
        self.figIndex = self.fig.number
        self.ax = self.fig.add_subplot(111)
        self.lines = {}    
        self.datax = {}
        self.datay = {}
        self.lineYBoundry = {}
        self.pointsToShow = pointsToShow

        self.ani = animation.FuncAnimation(self.fig, self.animate, interval=20)
        plt.show(block = False)
        plt.ylim([-1.1,1.1])


    def animate(self, i):
        for lineName in self.lines.keys():
            self.lines[lineName].set_data(self.datax[lineName],self.datay[lineName])
            self.chagneFigureBoundries(lineName)
            # self.refresh()
        return self.lines.values(),

    def isFigureOpen(self):
        return plt.fignum_exists(self.figIndex)
    
    def drawLine(self, lineName, x, y, lineStyle = 'r-'):
        self.datay[lineName] = y
        self.datax[lineName] = x
            
        # self.lines[lineName].set_data(x,y)
        # self.chagneFigureBoundries(x, y, lineName)
        # self.refresh()

        if lineName not in self.lines:
            newLine, = self.ax.plot(x, y, lineStyle)
            self.lines[lineName] = newLine

            plt.draw()
            # self.refresh()
            # line2, = ax.plot(x, a1, 'b-')
    
    def getBoundry(self, y, startIndex):
        minVal = np.min(y[startIndex:])
        maxVal = np.max(y[startIndex:])
        
        if abs(minVal) > abs(maxVal):
            boundry = abs(minVal)
        else:
            boundry = abs(maxVal)
        
        return boundry
    
    def chagneFigureBoundries(self, lineName):
        x = self.datax[lineName]  
        y = self.datay[lineName]
        startIndex = 0
        xEnd = x[-1]
        
        if len(x) >= self.pointsToShow:
            startIndex = len(x) - 1 - self.pointsToShow 
#        elif len(x) > 3:
#            xEnd = (x[2] - x[1]) * self.pointsToShow / 2 
#        
        xStart = x[startIndex]
        
        plt.xlim([xStart,xEnd])
        
        # boundry = self.getBoundry(y, startIndex)
        
        # self.lineYBoundry[lineName] = boundry
        
        # for b in self.lineYBoundry.values():
        #     if b > boundry:
        #         boundry = b
        
        # if (boundry > 0):
        #     plt.ylim([-boundry*1.1,boundry*1.1])
    
    def refresh(self):
        plt.pause(0.001)

# class plotterPg:
    # def __init__(self, pointsToShow = 10000):        
    #     plt.ion()    
    #     self.fig = plt.figure()
    #     self.figIndex = self.fig.number
    #     self.ax = self.fig.add_subplot(111)
    #     self.lines = {}    
    #     self.lineYBoundry = {}
    #     self.pointsToShow = pointsToShow

    # def isFigureOpen(self):
    #     return plt.fignum_exists(self.figIndex)
    
    # def drawLine(self, lineName, x, y, lineStyle = 'r-'):
    #     if lineName in self.lines:
    #         self.lines[lineName].set_data(x,y)
    #         self.chagneFigureBoundries(x, y, lineName)
    #     else:
    #         newLine, = self.ax.plot(x, y, lineStyle)
    #         self.lines[lineName] = newLine
    #         plt.show()
    #         # line2, = ax.plot(x, a1, 'b-')
    
    # def getBoundry(self, y, startIndex):
    #     minVal = np.min(y[startIndex:])
    #     maxVal = np.max(y[startIndex:])
        
    #     if abs(minVal) > abs(maxVal):
    #         boundry = abs(minVal)
    #     else:
    #         boundry = abs(maxVal)
        
    #     return boundry
    
    # def chagneFigureBoundries(self, x, y, lineName):
    #     startIndex = 0
    #     xEnd = x[-1]
        
    #     if len(x) >= self.pointsToShow:
    #         startIndex = len(x) - 1 - self.pointsToShow 
#        elif len(x) > 3:
#            xEnd = (x[2] - x[1]) * self.pointsToShow / 2 
#        
    #     xStart = x[startIndex]
        
    #     plt.xlim([xStart,xEnd])
        
    #     boundry = self.getBoundry(y, startIndex)
        
    #     self.lineYBoundry[lineName] = boundry
        
    #     for b in self.lineYBoundry.values():
    #         if b > boundry:
    #             boundry = b
        
    #     if (boundry > 0):
    #         plt.ylim([-boundry*1.1,boundry*1.1])
    
    # def refresh(self):
    #     plt.pause(0.01)
    
        