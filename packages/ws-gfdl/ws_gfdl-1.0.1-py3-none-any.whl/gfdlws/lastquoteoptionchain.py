import asyncio
import websockets
import os

url = None
key = None
exg = None
prd = None
exp = None
otp = None
srp = None


def get(ws, exchange, product, expiry=None, optiontype=None, strikeprice=None):
    if exchange == "":
        print("Exchange is mandatory.")
    else:
        exg = exchange

    if product == "":
        prd = ''
    else:
        prd = product

    if expiry == "":
        exp = ''
    else:
        exp = expiry

    if optiontype == "":
        otp = ''
    else:
        otp = optiontype

    if strikeprice == "":
        srp = ''
    else:
        srp = strikeprice

    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws, exg, prd, exp, otp, srp))
    return


async def mass_subscribe_n_stream(ws, exg, prd, exp, otp, srp):
    try:
        req_msg = '{"MessageType":"GetLastQuoteOptionChain","Exchange":"' + exg + '","Product":"' + prd + '"'
        if exp is not None:
            req_msg = req_msg + ',"Expiry":"' + exp + '"'
        if otp is not None:
            req_msg = req_msg + ',"optionType":"' + otp + '"'
        if srp is not None:
            req_msg = req_msg + ',"strikePrice":"' + srp + '"'

        req_msg = str(req_msg + '}')
        print("Request : " + req_msg)
        await ws.send(req_msg)
        await get_msg(ws)
    except:
        print('In Exception...' + str(os.error))
        return


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)