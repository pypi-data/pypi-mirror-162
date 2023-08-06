import asyncio
import websockets
import json
import errno
import os

exg = None


def get(ws, exchange, instrumenttype=None, product=None, expiry=None, optiontype=None):
    if exchange == "":
        print("Exchange is mandatory.")
    else:
        exg = exchange
    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws, exg, instrumenttype, product, expiry, optiontype))
    return


async def mass_subscribe_n_stream(ws, exg, ist, prd, exp, opt):
    try:
        req_msg = '{"MessageType":"GetStrikePrices", "Exchange":"' + exg + '"'
        # if ist is not None:
        #     req_msg = req_msg + '"Exchange":"' + exg + '"'
        if ist is not None:
            req_msg = req_msg + ',"InstrumentType":"' + ist + '"'
        if prd is not None:
            req_msg = req_msg + ',"Product":"' + prd + '"'
        if exp is not None:
            req_msg = req_msg + ',"Expiry":"' + exp + '"'

        req_msg = str(req_msg + '}')
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
