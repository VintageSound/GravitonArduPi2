
from server.dataAccess.clientListener import clientListener
import asyncio

async def listen():
    listener = clientListener()
    await listener.initSocket()

    try:
        while True:
            data, control, fit = await listener.waitForDataFromClient()
            print("data", data.time, data.data)
            print("control", control.time, control.data)
            print("fit", fit.time, fit.data)
    except Exception as ex:
        print(ex)

asyncio.run(listen())