import asyncio
import websockets

url = None
key = None
exg = None
sym = None
msg = None
prc = None
prd = None
iss = None


def get(ws, exchange, symbol, periodicity, period,isShortIdentifiers):
    exg = exchange
    sym = symbol
    prc = periodicity
    prd = period
    iss = isShortIdentifiers
    asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(ws, exg, sym, prc, prd, iss))
    return


async def mass_subscribe_n_stream(ws, exg, sym, prc, prd, iss):
    try:
        req_msg = str(
            '{"MessageType":"GetSnapshot","Exchange":"' + exg + '","Periodicity":"' + prc + '","Period":' + f'{prd}' + ',"isShortIdentifiers":"' + iss + '","InstrumentIdentifiers":' + sym + '}')
        await ws.send(req_msg)
        print("Request : " + req_msg)
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
