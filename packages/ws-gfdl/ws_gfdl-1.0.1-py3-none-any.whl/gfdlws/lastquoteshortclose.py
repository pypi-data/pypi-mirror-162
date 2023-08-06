import asyncio
import websockets

exg = None
sym = None
msg = None
ws = None


def get(ws, exchange, symbol, isShortIdentifier):
    exg = exchange
    sym = symbol
    isi = isShortIdentifier
    asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(ws, exg, sym, isi))
    return


async def mass_subscribe_n_stream(ws, exg, sym, isi):
    try:
        req_msg = str(
            '{"MessageType":"GetLastQuoteShortWithClose","Exchange":"' + exg + '","isShortIdentifier":"' + isi + '","InstrumentIdentifier":"' + sym + '"}')
        await ws.send(req_msg)
        print("Response : " + req_msg)
        await get_msg(ws)
    except:
        return msg


async def get_msg(ws):
    while True:
        try:
            message = await ws.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)