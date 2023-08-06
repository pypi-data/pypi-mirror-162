import asyncio
import websockets
import json

url = None
key = None
exg = None
sym = None
msg = None
ws = None


def connect(endpoint, apikey):
    ws = asyncio.get_event_loop().run_until_complete(mass_subscribe_n_stream(endpoint, apikey))
    return ws


async def mass_subscribe_n_stream(endpoint, apikey):
    ws = await asyncio.wait_for(websockets.connect(endpoint, max_size=2 ** 50), timeout=60)
    stst = await authenticate(ws, apikey)  # Authenticates the connection
    if stst == 'Key Authenticated!!!':
        return ws
    else:
        print('Not connected. Trying again. Please wait...')
        stst = await authenticate(ws, apikey)


async def authenticate(ws, key):
    try:
        msg = 'Performing Authentication'
        print(msg)
        authentication_msg = json.dumps({
            "MessageType": "Authenticate",
            "Password": key
        })
        authenticated = False
        await ws.send(authentication_msg)
        while not authenticated:  # Stay in this loop until successful authentication.
            response = await ws.recv()
            response = json.loads(response)
            print(response)
            if response['MessageType'] == "AuthenticateResult":
                if response['Complete']:
                    status = 'Key Authenticated!!!'
                    return status
                else:
                    print('Not connected. Trying again. Please wait...')
                    await ws.send(authentication_msg)
    except:
        return msg