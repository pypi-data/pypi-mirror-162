""" Classes to discover Zeptrion devices in the local network"""


from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf
from pyzeptrion.bulb import ZeptrionBulb
from typing import Any, Mapping, Optional, List
import logging
import asyncio

_TIMEOUT_MS = 3000

logger = logging.getLogger(__name__)

class ZeptrionZeroconfListener(object):
    """ Class to search the local network for Zeptrion devices using the zeroconf protocol"""
    def __init__(self) -> None:
        """Init the listener."""
        self.data = []


    def remove_service(self, zeroconf, type, name): print("Service %s removed" % (name,))

    def add_service(self, zeroconf, zeroconf_type, name):
        """Add a device that became visible via zeroconf."""
        asyncio.ensure_future(self.async_add_service(zeroconf, zeroconf_type, name))

    async def async_add_service(self, zeroconf, zeroconf_type, name):
        """Add a device that became visible via zeroconf."""
        info = AsyncServiceInfo(zeroconf_type, name)
        await info.async_request(zeroconf, _TIMEOUT_MS)
        self.data.append(info)
     
        
    update_service = add_service
    
    def get_data(self):
        return self.data

class ZeptrionRegistryDevice(object):
    """ Representation of a device in the registry"""

    def __init__(self,host: str, chn: int,type: str):
        self._host = host
        self._chn = chn
        self._type = type
    
    def __str__ (self):
        return "Host: {}\nChannel: {}\nType: {}\n".format(self._host, self._chn,self._type)
    
    @property
    def host(self) -> str:
        return self._host

    @property
    def chn(self) -> int:
        return self._chn

    @property
    def type(self) -> str:
        return self._type

class ZeptrionRegistry(object):
    """ Class to built a registry of Zeptrion devices"""
    def __init__ (self):
        self._devices= []

    @classmethod
    async def create_registry(self):
        myAsyncZeroconf = AsyncZeroconf()
        listener = ZeptrionZeroconfListener()
        service_browser = AsyncServiceBrowser(myAsyncZeroconf.zeroconf, "_zapp._tcp.local.", listener) 
        await asyncio.sleep(5)
        self._devices = []

        try:
            for info in listener.get_data():
                host = info.parsed_addresses()[0]
                channels = str(info.properties[b'type']).split("-")[1]
                for chn in range(int(channels)):
                    tempDevice = await ZeptrionBulb.create(host,str(chn+1))
                    if tempDevice._type !="NaN":
                       device = ZeptrionRegistryDevice(host,chn+1,tempDevice._type)
                       self._devices.append(device)
                    await tempDevice.close()   
                    del tempDevice            
                       
        finally:
            await service_browser.async_cancel()
            if not myAsyncZeroconf :
                await myAsyncZeroconf.close() 
        
        self._devices.sort(key=lambda x: x._type)
        return self
    
    async def get_devices(self):
        return self._devices