
import sys

import logging

import asyncio

import aiocoap
import aiocoap.resource as resource


class CoApNode:
    """ """
    def __init__(self, name, addr):  
        self.deviceName = name
        self.ipAddr = addr

    ipAddr = 0
    deviceName = " "

class deviceList:

    deviceList = []

    def printDeviceList(self):
        original_stdout = sys.stdout
        with open('node_directory.txt', 'w') as f:
            sys.stdout = f
            for x in self.deviceList:
                print("%")
                print(" -"+x.deviceName)
                print(" -"+x.ipAddr)
            print("#")
            print(" ")
            sys.stdout = original_stdout
            print("New list has been written to node_directory.txt")

listt = deviceList

class NewNodeAddrResource(resource.Resource):
    """ When a node joins the network, it pus its ipv6 address and device name to this resource. Payload format is: 'Device1,fd11:22:0:0:fec7:c8ff:c86a:a009' """

    def addNode(self, nodeInfo):
        global listt  

        # get coap node info
        index = 1
        name = ""
        addr = ""
        for x in nodeInfo: # get device name
            if x != ',':
                name = name + x
                index = index+1
            else:
                break
        for x in nodeInfo[index:]: # get IP address
            addr = addr + x
        tempNode = CoApNode(name, addr) # tempNode holds the received node data

        # check if the device name is already inthe list. If so, update its IP address
        newNode = 1 # assume the device name is new
        for x in listt.deviceList:
            if x.deviceName == tempNode.deviceName:
                x.ipAddr = tempNode.ipAddr
                newNode = 0 # device name is already in the lists
        if newNode == 1: #if the device name is new, add the node info to the list
            listt.deviceList.append(tempNode)
        listt.printDeviceList(self=listt) # print the list to the file
        return newNode
        
    def set_content(self, content):
        self.content = content
    
    async def render_get(self, request):
        print('GET request')
        return aiocoap.Message(payload=self.content)
 
    async def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.set_content(request.payload)
        nodeIsNew = self.addNode(request.payload.decode("utf-8"))
        if (nodeIsNew):
            payload = b"1"
        else:
            payload = b"0"
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def initList():
    global listt
    name = ""
    addr = ""
    index = 0

    with open('node_directory.txt', 'r') as f:
        while True:
            line = f.readline()
            if (not line) or (line == "#\n"):
                break
            elif line == "%\n":
                line = f.readline()
                name = line[2:-1]
                line = f.readline()
                addr = line[2:-1]
                tempNode = CoApNode(name, addr)
                listt.deviceList.append(tempNode)
                index = index + 1
        print("Added "+ str(index) + " nodes from directory file.")


async def main():

    initList()

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