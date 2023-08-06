import asyncio
import websockets
import json
import errno
import os

url = None
key = None
exg = None


def get(ws, exchange):
    if exchange == "":
        print("Exchange is mandatory.")
    else:
        exg = exchange

    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws, exg))
    return


async def mass_subscribe_n_stream(ws, exg):
    try:
        req_msg = str(
            '{"MessageType":"GetExchangeMessages","Exchange":"' + exg + '"}')
        await ws.send(req_msg)
        print("Response : " + req_msg)
        await get_msg(ws)
    except:
        return "Error"


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)
