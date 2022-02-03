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
        control = timeDataTuple(jsonData["control"]["time"], jsonData["control"]["data"])
        fit = timeDataTuple(jsonData["fit"]["time"], jsonData["fit"]["data"])
        
        return data, control, fit

# asyncio.run(main())