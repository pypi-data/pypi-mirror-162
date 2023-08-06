import asyncio
import websockets

url = None
key = None
exg = None
sym = None
msg = None


def get(ws, exchange, symbol):
    exg = exchange
    sym = symbol
    asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(ws, exg, sym))
    return


def stop(ws, exchange, symbol):
    exg = exchange
    sym = symbol
    asyncio.get_event_loop().run_until_complete(mass_unsubscribe_n_stream(ws, exg, sym))
    return


async def mass_subscribe_n_stream(ws, exg, sym):
    req_msg = str('{"MessageType":"SubscribeRealtime","Exchange":"' + exg + '","Unsubscribe":"false","InstrumentIdentifier":"' + sym + '"}')
    print("Request : " + req_msg)
    await ws.send(req_msg)
    await get_msg(ws)
    return


async def mass_unsubscribe_n_stream(ws, exg, sym):
    req_msg = str('{"MessageType":"SubscribeRealtime","Exchange":"' + exg + '","Unsubscribe":"true","InstrumentIdentifier":"' + sym + '"}')
    print("Request : " + req_msg)
    await ws.send(req_msg)
    await get_msg(ws)
    return


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)