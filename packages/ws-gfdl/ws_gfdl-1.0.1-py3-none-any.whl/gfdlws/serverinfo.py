import asyncio
import websockets
import json
import errno
import os


def get(ws):
    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws))
    return


async def mass_subscribe_n_stream(ws):
    try:
        req_msg = str('{"MessageType":"GetServerInfo"}')
        await ws.send(req_msg)
        print("Request : " + req_msg)
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
