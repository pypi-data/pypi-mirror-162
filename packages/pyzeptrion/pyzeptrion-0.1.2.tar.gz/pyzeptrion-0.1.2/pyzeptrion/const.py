""" Definition of constants used in the library """

TIMEOUT = 15

""" URLs to call the Zeptrion API """
GET_STATE_URL = "/zrap/chscan/ch"
GET_DESC_URL = "/zrap/chdes/ch"
POST_CTRL_URL = "/zrap/chctrl/ch"

""" Commends for the bulb """
BULB_ON="on"
BULB_OFF="off"
BULB_TOGGLE="toggle"
BULB_DIMUP="dim_up"
BULB_DIMDOWN="dim_down"


""" commands for the blind """
BLIND_CLOSE="move_close"
BLIND_OPEN="move_open"
BLIND_STOP="stop"


""" 
Zeptrion device types.
This is not documented in the API docs, Found through reverse engineering
"""
device_types = {"-1":"NaN", "1": "Bulb on/off","3":"Bulb dimmable", "5":"Blind", "6":"Blind"}
