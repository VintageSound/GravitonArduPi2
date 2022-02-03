
# arr = [0,1,2,3,4,5,6,7]
# print(arr[0:3])

num =101


bytesarr = b'12345e'


print(bytesarr[2].to_bytes(length=1,byteorder='big'))
print(bytesarr[0:2])
print(bytesarr[4:])
print(bytesarr[0])
print(bytesarr.endswith(b'e'))

# from numpy.lib.function_base import average
# from plotter import *
# from time import time
# from time import sleep
# import numpy as np 
# import gc
# import matplotlib.pyplot as plt
# from ADSAccess.ADSAccessManger import ADSAccessManger
# import threading
# import operator


# def collectData():
#     i = 0
#     ads = ADSAccessManger(sps=10, gain = 0)
#     # ads.increaseEfficiency()

#     while 1:
#         newT, newX = ads.readChannel(0)
#         if not np.isnan(newX):
#             with _lock:   
#                 x.append(newX)
#                 tx.append(newT)
#         else:
#             with _lock:
#                 errorCount.append(newX)

#         # newTy, newY = ads.readChannel(2)
#         # if not np.isnan(newY):
#         #     with _lock:
#         #         x.append(newY)
#         #         tx.append(newTy)
#         # else:
#         #     with _lock:
#         #         errorCount.append(newX)
                
#         i = i + 1
    
# gc.collect()
# # plt.ion()    
# # fig = plt.figure()
# # ax = fig.add_subplot(111)

# # print("hello word")

# # ads = ADSAccessManger()

# plot = plotter(100)
# x = []
# y = []
# tx = []
# ty = []  
# errorCount = []

# _lock = threading.Lock()
# thrd = threading.Thread(target=collectData)
# thrd.start()

# while 1:
#     if len(x) == 0:
#         continue

#     with _lock:
#         # if len(x) > 0:
#         # print(x)
#         txcopy = tx.copy()
#         xcopy = x.copy()
#         print("error count: " + str(len(errorCount)))
#         errorCount.clear()
#         tx.clear()
#         x.clear()

#     dt = list(map(operator.sub, txcopy[1:-1], txcopy[0:-2]) )
#     print("actaul reading time: " + str(average(dt)))
#     print(xcopy)


#     # plot.drawLine('x',txcopy,xcopy,'r.')
#     # plot.refresh()
#     sleep(0.5)

# # while 1:
# #     txNew, xNew = ads.readChannel(0)
# #     # tyNew, yNew = ads.readChannel(1)
# #     print(str(txNew) + ", "+ str(xNew))
# #     tx.append(txNew)
# #     x.append(xNew)

# #     # ty.append(tyNew)
# #     # y.append(yNew)
    
# #     # plot.drawLine('y',ty,y,'b.')
# #     plot.drawLine('x',tx,x,'r.')
