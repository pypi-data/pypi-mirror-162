""" Class to represent a blind attached to a Zeptrion device """

"""
Supported functions:
- move_open
- move_close
- stop
"""

import aiohttp
import logging
from pyzeptrion.device import ZeptrionDevice
from pyzeptrion.const import device_types, BLIND_CLOSE, BLIND_OPEN, BLIND_STOP


_LOGGER = logging.getLogger(__name__)

class ZeptrionBlind(ZeptrionDevice):
    """A class for a Zeptrion blinds derived from the ZeptrionDevice class."""
    def __init__(self,host: str, chn: int, session: aiohttp.client.ClientSession = None,):
       super().__init__(host, chn,session)
    
    @classmethod
    async def create(self, host, chn):
        """ Called before __init__ to assign values to the object created"""
        self = ZeptrionBlind(host, chn)
        await self._set_description()
        mybase = await self._set_state()
        self._state=BLIND_OPEN if int(mybase[0][0].text) > 0 else BLIND_CLOSE
        return self
        
    async def move_open(self):
        """ open the blind """
        response = await self.request(
             uri=self._post_ctrl_uri, method="POST", data={"cmd": BLIND_OPEN})
        self._state=BLIND_OPEN
        return response

    async def move_close(self):
        """ close the blind """
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BLIND_CLOSE})
        self._state=BLIND_CLOSE
        return response

    async def stop(self):
        """ stop moving the blind """
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BLIND_STOP})
        self._state=BLIND_STOP
        return response


    """ Session handling"""
    async def close(self) -> None:
      
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "ZeptrionBlind":
     
        return self

    async def __aexit__(self, *exc_info) -> None:
    
        await self.close()
