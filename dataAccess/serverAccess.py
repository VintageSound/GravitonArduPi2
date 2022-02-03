import gc
import asyncio
import asyncudp
import json
from dataStructures.timeDataTuple import timeDataTuple

class serverAccess:
    def __init__(self):
        self.ip = '169.254.200.205'
        self.port = 9999

    def convertDatatoJsonString(self, data, control, fit):
        dictinary = {}

        data.checkIfTupleValid()
        control.checkIfTupleValid()
        fit.checkIfTupleValid()
        
        dictinary["data"] = {"data" : data.data, "time" : data.time }
        dictinary["control"] = {"data" : control.data, "time" : control.time }
        dictinary["fit"] = {"data" : fit.data, "time" : fit.time }
        return json.dumps(dictinary)

    async def sendDataToServer(self, data, control, fit):
        jsonStr = self.convertDatatoJsonString(data, control, fit)
        await self._sendDataToServer(jsonStr)

    async def _sendDataToServer(self, jsonData):
        try:
            dataBytes = bytes(jsonData,encoding="utf-8")
            sock = await asyncudp.create_socket(remote_addr=(self.ip, self.port))
            sock.sendto(dataBytes)
            # print(await sock.recvfrom())
        except Exception as ex:
            print(ex)
        finally:
            sock.close()

# a = serverAccess()
# t = timeDataTuple([1,2,3,4,5],[6,7,8,9,10])
# jsonStr = a.convertDatatoBytes(t,t,t)
# print(jsonStr)

# j = json.loads(jsonStr)
# pass 