import asyncio
import websockets
from datetime import datetime
import json
import time
import errno

url = None
key = None
exg = None
sym = None
msg = None


def get(ws):
    asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(ws))
    return


async def mass_subscribe_n_stream(ws):
    try:
        req_msg = str('{"MessageType":"GetExchanges"}')
        await ws.send(req_msg)
        print(req_msg)
        await get_msg(ws)  # Listens for the tick data until market close
    except:
        return msg


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)
