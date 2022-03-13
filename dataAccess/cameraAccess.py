from dataStructures.timeDataTuple import timeDataTuple
import time
import numpy as np
import cv2

class cameraAccess:
    def __init__(self):
        self.isInitialized = False
        self.video = None
        
    def waitForInitialization(self):
        print("initializing camera...")
        
        time.sleep(1)
        self.video = cv2.VideoCapture(0)
        
        self.width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.middle = 0
        
        # Junk code to burn through the first few images that the
        # camera produces.  If you don't do this, then you get blank images
        for i in range(0,5):
            ret, frame = self.video.read()
            time.sleep(0.5)
            
        self.startTime = time.time()
        self.isInitialized = True
        print("camera initialized")
    
    def _getElapsedTime(self):
        return time.time() - self.startTime
    
    def readData(self):
        if not self.isInitialized or self.video is None:
            return None
        
        time.sleep(1)
        
        ret, frame = self.video.read()

        t = self._getElapsedTime()
        
        if frame is None:
            print ("frame is None")
            return timeDataTuple([t], [0]) 
        
        pixelPositions = np.argwhere(frame[:,:,2]>250)
        
        if len(pixelPositions) == 0:
            meanX = 0
        else:
            meanX = np.average(pixelPositions[:,1],axis=0)
            
        meanX = meanX * 10 / self.width
        
        # Set the middle postion for the first time to be the first data point
        if self.middle == 0 and meanX != 0:
            self.middle = meanX
            
        meanX -= self.middle 
        meanX *= -1
        
        return timeDataTuple([t], [meanX])
    
    def close(self):
        print("closing camera")
        self.isInitialized = False
        self.video.release()
        self.video = None
        cv2.destroyAllWindows()
