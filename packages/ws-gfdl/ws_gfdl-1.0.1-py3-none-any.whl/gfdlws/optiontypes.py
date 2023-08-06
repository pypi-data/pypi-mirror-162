import asyncio
import websockets
import json
import errno
import os

ist = None
prd = None
exg = None
exp = None


def get(ws, exchange, InstrumentType=None, Product=None, Expiry=None):
    if exchange == "":
        print("Exchange is mandatory.")
    else:
        exg = exchange

    ist = InstrumentType
    prd = Product
    exp = Expiry
    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws, exg, ist, prd, exp))
    return


async def mass_subscribe_n_stream(ws, exg, ist, prd, exp):
    try:
        print("1")
        req_msg = '{"MessageType":"GetOptionTypes","Exchange":"' + exg + '"'
        # if exg != "":
        #     req_msg = req_msg + '"Exchange":"' + exg + '"'
        if ist is not None:
            req_msg = req_msg + ',"InstrumentType":"' + ist + '"'
        if prd  is not None:
            req_msg = req_msg + ',"Product":"' + prd + '"'
        if exp  is not None:
            req_msg = req_msg + ',"Expiry":"' + exp + '"'
        print("2")
        req_msg = str(req_msg + '}')
        await ws.send(req_msg)
        print("Response : " + req_msg)
        await get_msg(ws)
        print("4")
    except:
        return "Error"


async def get_msg(ws):
    print("3")
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)
