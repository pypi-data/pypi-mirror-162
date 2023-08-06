import asyncio
import websockets
import json
import errno
import os

url = None
key = None
exg = None
prc = None
prd = None
ist = None
dfm = None
dto = None
ntr = None


def get(ws, exchange, periodicity, period, instrumentType=None, dfrom=None, dto=None, nonTraded=None):
    # if endpoint == "":
    #     print("Endpoint is mandatory.")
    # else:
    #     url = endpoint
    #
    # if apikey == "":
    #     print("APIkey is mandatory.")
    # else:
    #     key = apikey

    if exchange == "":
        print("Exchange is mandatory.")
    else:
        exg = exchange

    if periodicity == "":
        prc = ''
    else:
        prc = periodicity

    if period == "":
        prd = ''
    else:
        prd = period

    if instrumentType == "":
        ist = ''
    else:
        ist = instrumentType

    if dfrom == "":
        dfm = ''
    else:
        dfm = dfrom

    if nonTraded == "":
        ntr = ''
    else:
        ntr = nonTraded
    # endpoint, apikey, exchange, periodicity, period, instrumentType, dfrom, dto, nonTraded
    asyncio.get_event_loop().run_until_complete(
        mass_subscribe_n_stream(ws, exg, prc, prd, ist, dfm, dto, ntr))
    return


async def mass_subscribe_n_stream(ws, exg, prc, prd, ist, dfm, dto, ntr):
    try:
        req_msg = '{"MessageType":"GetExchangeSnapshot","Exchange":"' + exg + '","periodicity":"' + prc + '","period":"' + prd + '"'
        if ist is not None:
            req_msg = req_msg + ',"instrumentType":"' + ist + '"'
        if dfm is not None:
            req_msg = req_msg + ',"From":"' + dfm + '"'
        if dto is not None:
            req_msg = req_msg + ',"To":"' + dto + '"'
        if ntr is not None:
            req_msg = req_msg + ',"nonTraded":"' + ntr + '"'
        req_msg = str(req_msg + '}')
        print("Request : " + req_msg)
        await ws.send(req_msg)
        await get_msg(ws)
    except:
        print('Exception...' + str(os.error))
        return


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)
