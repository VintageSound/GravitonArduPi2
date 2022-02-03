import asyncio
import json
import asyncudp
from dataStructures.timeDataTuple import timeDataTuple

class clientListener:
    def __init__(self):
        pass

    async def initSocket(self):
        self.sock = await asyncudp.create_socket(local_addr=('0.0.0.0', 9999))

    async def waitForDataFromClient(self):
        data, addr = await self.sock.recvfrom()
        jsonData = json.loads(data)
        data = timeDataTuple(jsonData["data"]["time"], jsonData["data"]["data"])

        if len(data.time) != len(data.data):
            raise Exception("invalid data recived") 

        control = timeDataTuple(jsonData["control"]["time"], jsonData["control"]["data"])

        if len(control.time) != len(control.data):
            raise Exception("invalid control data recived") 

        fit = timeDataTuple(jsonData["fit"]["time"], jsonData["fit"]["data"])
        
        if len(fit.time) != len(fit.data):
            raise Exception("invalid fit data recived") 


        return data, control, fit

# asyncio.run(main())