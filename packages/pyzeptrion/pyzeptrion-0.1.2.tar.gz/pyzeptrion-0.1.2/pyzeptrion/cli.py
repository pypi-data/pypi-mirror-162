"""
Command line interface for the pyzeptrion library.
The first step is always to gather all Zeptrion devices in the network (like
using the "discover" function)
So only devices in the actual network can be used in the cli

Examples:
Discover all Zeptrion devices in network
python3 -m pyzeptrion.cli discover

Turn on bulb
python3 -m pyzeptrion.cli set -a 192.168.0.181 -c 1 -p on

Close Blind
python3 -m pyzeptrion.cli set -a 192.168.0.185 -c 2 -p move_close

If you use a command like "on" for a blind, you'll receive an error message.
"""

import argparse
import asyncio

from pyzeptrion.blind import ZeptrionBlind
from pyzeptrion.bulb import ZeptrionBulb
from pyzeptrion.discover import ZeptrionRegistry
from .const import device_types, BULB_ON, BULB_OFF, BULB_DIMDOWN, BULB_DIMUP, BULB_TOGGLE, BLIND_CLOSE, BLIND_OPEN, BLIND_STOP, TIMEOUT

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='"set" or "discover"')
    parser.add_argument('-a', '--address', help='device ip address')
    parser.add_argument('-c', '--channel', type = int, help='channel of the device')
    parser.add_argument('-p', '--params', help='allowed commands, "on", "off", "toggle", "stop", "move_open". "move_close"')
    
    myRegistry = await ZeptrionRegistry.create_registry()
    devices = await myRegistry.get_devices(myRegistry) 
    
    args = parser.parse_args()

    if args.action == 'discover':
        for device in devices:
            print(device)
        
    
    elif args.action == 'set':
        if args.address is None:
            return print('IP address is empty.')
        if args.channel is None:
            return print('Channel is empty.')
        if args.params is None:
            return print('Channel is empty.')
        
        tempDevice = None
        for device in devices:
            if args.address == device.host and args.channel == device.chn:
                print("Found a Zeptrion device matching the IP and Channel in the registry:")
                print(device)
                if device.type == "Blind":
                        tempDevice = await ZeptrionBlind.create(args.address,str(args.channel))
                        break
                else:
                        tempDevice = await ZeptrionBulb.create(args.address,str(args.channel))
                        break
        else:
                return print("no device found")
        
        if tempDevice != None: 
            if (tempDevice.type == "Blind" and args.params in [BLIND_CLOSE, BLIND_OPEN, BLIND_STOP]) or (tempDevice.type in ["Bulb on/off","Bulb dimmable"] and args.params in [BULB_DIMDOWN, BULB_DIMUP, BULB_OFF, BULB_ON, BULB_TOGGLE]):
               await tempDevice.post_cmd(args.params) 
            else:
                print("Parameter",args.params," can not be used on", tempDevice.type)
                await tempDevice.close()   
                del tempDevice
                return 
        print("Succesfully changed the state of the device!")
        print(tempDevice)
        await tempDevice.close()   
        del tempDevice      
              

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
