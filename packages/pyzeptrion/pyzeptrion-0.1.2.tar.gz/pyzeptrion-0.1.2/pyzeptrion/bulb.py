"""Class to represent a bulb attaches to a Zeptrion device"""
import aiohttp
import logging
from pyzeptrion.device import ZeptrionDevice
from pyzeptrion.const import BULB_DIMDOWN, BULB_DIMUP, BULB_OFF, BULB_ON

_LOGGER = logging.getLogger(__name__)



class ZeptrionBulb(ZeptrionDevice):
    """A class for a Zeptrion bulb, derived from the ZetprionDevice class."""
    
    def __init__(self,host: str, chn: int, session: aiohttp.client.ClientSession = None,):
       super().__init__(host,chn,session)
    
    @classmethod
    async def create(self, host, chn):
        """ Called before __init__ to assign values to the object"""
        self = ZeptrionBulb(host, chn)
        await self._set_description()
        mybase = await self._set_state()
        self._state=BULB_ON if int(mybase[0][0].text) > 0 else BULB_OFF
        return self

    async def set_on(self):
        """ turn the bulb on and update state"""
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_ON})
        self._state=BULB_ON
        return response

    async def set_off(self):
        """ turn the bulb off and update state"""
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_OFF})
        self._state=BULB_OFF
        return response

    async def dim_down(self):
        """ dim the bulb down """
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_DIMDOWN})
        self._state=BULB_ON
        return response

    async def dim_up(self):
        """ dim the bulp up"""
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_DIMUP})
        self._state=BULB_ON
        return response

    async def dim_down_t(self, t:int):
        """ dim the bulb down for t milliseconds"""
        if 100 <= t <= 32000:
            response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_DIMDOWN+"_("+str(t)+")"})
            self._state=BULB_ON
        return response

    async def dim_up_t(self, t:int):
        """ dim the bulb up for t milliseconds"""
        if 100 <= t <= 32000:
            response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_DIMUP+"_("+str(t)+")"})
            self._state=BULB_ON
        return response

    async def dim_t(self, t:int):
        """ dim the bulb in either direction for t milliseconds """
        if 100 <= t <= 32000:
            response = await self.request(
            ri=self._post_ctrl_uri, method="POST", data={"cmd": BULB_DIMUP+"_("+str(t)+")"})
            self._state=BULB_ON
        return response

    async def toggle(self):
        """ toggle the bulb from on to off and vice-versa """
        cmd = BULB_OFF if self._state == BULB_ON else BULB_ON
        response = await self.request(
            uri=self._post_ctrl_uri, method="POST", data={"cmd": cmd})
        self._state=cmd
        return response

    """ Session handling"""
    async def close(self) -> None:
      
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "ZeptrionBulb":
     
        return self

    async def __aexit__(self, *exc_info) -> None:
    
        await self.close()
    
