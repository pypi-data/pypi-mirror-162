import asyncio
import websockets


exg = None
sym = None
msg = None
isi = None


def get(ws, exchange, symbols,isShortIdentifiers):
    exg = exchange
    sym = symbols
    isi = isShortIdentifiers
    asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(ws, exg, sym, isi))
    return


async def mass_subscribe_n_stream(ws, exg, sym, isi):
    try:
        req_msg = str('{"MessageType":"GetLastQuoteArray","Exchange":"' + exg + '","isShortIdentifiers":"' + isi + '","InstrumentIdentifiers":' + str(sym) + '}')
        await ws.send(req_msg)
        print("Request : " + req_msg)
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
