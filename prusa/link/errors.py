"""Prusa Link error states.html

For more information see prusa-link_states.txt.
"""

from prusa.connect.printer.errors import ErrorState, INTERNET, HTTP, TOKEN, API

assert HTTP is not None
assert TOKEN is not None

DEVICE = ErrorState("Device", "Ethernet or WIFI device does not exist")
PHY = ErrorState("Phy", "Eth|Wifi device is not connect", prev=DEVICE)
LAN = ErrorState("Lan", "Device has assigned IP", prev=PHY)

INTERNET.prev = LAN

SERIAL = ErrorState("Port", "Serial device does not exist")
RPI_ENABLED = ErrorState("RPIenabled", "RPI port is not enabled", prev=SERIAL)
ID = ErrorState("ID", "Not a Prusa printer", prev=RPI_ENABLED)
FW = ErrorState("Firmware", "Firmware is not up-to-date", prev=ID)
SN = ErrorState("SN", "Serial number can be read", prev=FW)

# first and last elements for all available error state chains
HEADS = [SERIAL, DEVICE]
TAILS = [SN, API]


def status():
    """Return a dict with representation of all current error states """
    result = []
    for head in HEADS:
        chain = {}
        current = head
        while current is not None:
            chain[current.name] = (current.ok, current.long_msg)
            current = current.next
        result.append(chain)
    return result
