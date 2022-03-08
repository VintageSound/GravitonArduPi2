import serial
import time
import numpy as np
import cv2

class cameraAccess:
    def __init__(self):
        pass


    def getPosition(self):
        ret,img = vid.read()


        PixelPositions = np.argwhere(img[:,:,2]>250)
        x_ave = np.average(PixelPositions[:,1],axis=0)
        if len(PixelPositions)==0:
            x_ave=0


        #dist=maxPixelPosition%width
        cv2.imshow('Frame',img)

        #cv2.imwrite('img.png',img)

        cv2.waitKey(10)

        return x_ave
