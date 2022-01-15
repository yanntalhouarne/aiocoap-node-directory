
import logging

import asyncio

import aiocoap
import aiocoap.resource as resource


class NewNodeAddrResource(resource.Resource):
    """ When a node joins the network, it pus its ipv6 address and device name to this resource. Payload format is: 'Device1,fd11:22:0:0:fec7:c8ff:c86a:a009' """
    
    def set_content(self, content):
        self.content = content
    
    async def render_get(self, request):
        print('GET request')
        return aiocoap.Message(payload=self.content)
 
    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

async def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(['.well-known', 'core'],
            resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['other', 'newNode'], NewNodeAddrResource())

    await aiocoap.Context.create_server_context(root)

    # Run forever
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())