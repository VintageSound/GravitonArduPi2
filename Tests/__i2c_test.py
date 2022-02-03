
#  Raspberry Pi Master for Arduino Slave
#  i2c_master_pi.py
#  Connects to Arduino via I2C
  
#  DroneBot Workshop 2019
#  https://dronebotworkshop.com
import sys
sys.path.append('/home/pi/Documents/GitProjects/GravitonArduPi')
print(sys.path)
from smbus import SMBus
import time
import struct
from utilities import plotter

addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1
dt = 0.001
pre_time = time.time()

while True:
	try:
		data = bus.read_i2c_block_data(addr,0,4)
		# val = struct.unpack("<l",bytearray(data[0:4]))
		# timeval = struct.unpack("<l",bytearray(data[4:]))
		# print(val)
		print(data); # val[0], timeval[0])
		
		# if dt > 0:
		# 	print("sps:",(1/dt))
		# 	time.sleep(dt)
		# 	dt -= 0.0001
		# else:

		time.sleep(0.01)
		dt = time.time() - pre_time

		print("sps: ", 1/dt)
	
		
		pre_time = time.time()
	except Exception as ex:
		print("Error... ", ex)

	

	