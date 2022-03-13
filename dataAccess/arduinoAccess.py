from dataStructures.timeDataTuple import timeDataTuple
import numpy as np
import spidev
import RPi.GPIO as GPIO
from time import sleep
from time import time
import sys
import os
import signal
import gc
from smbus import SMBus
import struct
import serial
import queue

class DecodingError(Exception):
    pass

class arduinoAccess:
    def __init__(self, sps = 8, gain = 0):
        self.ser = None
        self.isInitialized = False
        self.operationVoltage = 2
        # self.addr = 0x8 # bus address
        # self.bus = SMBus(1) # indicates /dev/ic2-1

    def waitForInitialization(self):
        print("waiting for arduino to initalize...")
        
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.ser.reset_input_buffer()
        sleep(3)
        
        while self.ser.in_waiting == 0:
            pass

        self.ser.read_until(expected=b'sssss')
        self.ser.read(size=5)
        
        self.isInitialized = True
        print("arduino initailized!")

    def readData(self):
        if self.ser.in_waiting == 0 or not self.isInitialized:
            return None
        
        timeArray = []
        dataArray = []

        try:
            rawData = self.ser.read(size=9)
            # print(rawData)
            
            if not rawData.endswith(b'e'):
                raise DecodingError("unexpected ending byte: " , rawData[8:])

            time = struct.unpack("<I",rawData[0:4])[0]
            data = struct.unpack("<i",rawData[4:8])[0]                

            time = time/1E3
            data = data/(2**31) * self.operationVoltage

            # print(rawData[0:4].hex())
            # print("time=",time)
            # print("data=",data)

            if np.isnan(time) or np.isnan(data):
                raise Exception()

            timeArray.append(time)
            dataArray.append(data)
        except DecodingError as e:
            print(e)
            print("faulty data: ", rawData)
            self.ser.read_until(expected=b'e')
        except Exception as e:
            print(e)
            print("faulty data: ", rawData)      

        return timeDataTuple(timeArray, dataArray)
        # rawData = self.bus.read_i2c_block_data(self.addr,0,32)
        # ulong = struct.unpack("<I",bytearray(rawData))[0]
        # value = self._toSigned32(ulong)

        # return value
 
    def close(self):
        self.isInitialized = False
        self.ser.close()
        gc.collect()
        gc.enable()
        GPIO.cleanup()

    def _toSigned32(self, n):
        n = n & 0xffffffff
        return (n ^ 0x80000000) - 0x80000000

