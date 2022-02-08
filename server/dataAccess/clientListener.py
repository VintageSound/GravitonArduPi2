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
        data = timeDataTuple(jsonData["data"]["time"].copy(), jsonData["data"]["data"].copy())
        data.checkIfTupleValid()
        
        control = timeDataTuple(jsonData["control"]["time"].copy(), jsonData["control"]["data"].copy())
        control.checkIfTupleValid()

        fit = timeDataTuple(jsonData["fit"]["time"].copy(), jsonData["fit"]["data"].copy())
        fit.checkIfTupleValid()

        return data, control, fit

# asyncio.run(main())