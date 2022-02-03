import serial

ser = serial.Serial('/dev/ttyACM0', 250000, timeout=1)
ser.reset_input_buffer()

while True:
    if ser.in_waiting > 0:
        rawData = ser.read_all().splitlines()
        
        for line in rawData:
            timeanddata = line.split(b',')

            if len(timeanddata) > 1:
                print("time = ", timeanddata[0].decode('utf-8'))
                print("data = ", timeanddata[1].decode('utf-8'))
            else:
                print("error: ", timeanddata)
        # data = ser.read_until('data')
        # print("data=",data,'\n')
        
        