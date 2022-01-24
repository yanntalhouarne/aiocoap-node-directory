import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)

async def main():

    context = await Context.create_client_context()

    await asyncio.sleep(2)
    #coap-client -m put coap://[2601:441:4d00:a470:ff73:a515:89c:f690]/other/newNode -t binary -f nodeInfo.txt
    payload = b"Device10,fd11:22:0:0:fec7:c8ff:c86a:a088"
    request = Message(code=PUT, payload=payload, uri="coap://[2601:441:4d00:a470:ff73:a515:89c:f690]/other/newNode")

    response = await context.request(request).response

    print('Result: %s\n%r'%(response.code, response.payload))
    if response.payload == b"1":
        print("Device added to directory.")
    else:
        print("Device's address updated in directory.")

if __name__ == "__main__":
    asyncio.run(main())