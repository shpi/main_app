from typing import Callable, NamedTuple, Optional, Union
from PySide2.QtCore import Property, __version_info__
import socket
from re import compile

"""
    # Perfect world as with Python's own 'property' (since 5.15.2):
    @Property(int, notify=nightmodeChanged)
    def function(self):
        getter_code

    @function.setter
    def function(self, value):
        setter_code


    # Setter layout until 5.15.1 (different function name required)
    @function.setter
    def set_function(self, value):
        setter_code


    # Fix for all versions
    def function(self):
        getter_code

    @Pre_5_15_2_fix(function, int, notify=nightmodeChanged)
    def function(self, value):
        setter_code


    Use this decorator only on setter functions which have the same name. Keep getter function undecorated.
    
    For read only properties just use regular @Property on getter as usual.
"""


def Pre_5_15_2_fix(type: type,
                   fget: Callable = None,
                   freset: Callable = None,
                   fdel: Callable = None,
                   doc='',
                   notify: Callable = None,
                   designable=True,
                   scriptable=True,
                   stored=True,
                   user=False,
                   constant=False,
                   final=False
                   ):
    """
    Use this decorator only on setter functions which have the same name.
    Keep getter function undecorated.

    For read only properties just use regular @Property on getter as usual.
    """

    def setter_fix(setter_func):
        if __version_info__ < (5, 15, 2):  # PySide2 < (5, 15, 2):
            # Function name MUST be DIFFERENT from getter's name
            # Create new function which has another name
            def dummy_function_with_other_name(*args, **kwargs):
                # Call setter function
                setter_func(*args, **kwargs)

            fset = dummy_function_with_other_name

        else:  # PySide2 >= (5, 15, 2)
            # Function name MUST be EQUAL to getter's name.
            # Passthrough original setter_func
            fset = setter_func

        # Create full Property in just one call!
        return Property(
            type=type,
            fget=fget,
            fset=fset,
            freset=freset,
            fdel=fdel,
            doc=doc,
            notify=notify,
            designable=designable,
            scriptable=scriptable,
            stored=stored,
            user=user,
            constant=constant,
            final=final
        )

    return setter_fix


SIOCGIFNETMASK = 0x891b
SIOCGIFHWADDR = 0x8927
SIOCGIFADDR = 0x8915


class IPEndpoint(NamedTuple):
    ip: str
    hostname: str
    mac: Optional[str] = None
    oui: Optional[str] = None
    iface: Optional[str] = None

    def __repr__(self):
        return f"{self.ip}: {self.hostname} [{self.mac}, {self.oui}]"


def lookup_oui(mac: Union[bytes, str]) -> str:
    file_path = "/usr/share/nmap/nmap-mac-prefixes"

    if type(mac) is bytes:
        mac = "".join(['%02X' % byte for byte in mac])
    elif type(mac) is str:
        mac = mac.replace(":", "")
    else:
        raise ValueError("mac must be bytes or string")

    mac = mac[:6].upper()

    # 887E25 Extreme Networks
    matcher = compile(f"^{mac} (.*)$")
    # Caching in a dict: +5MB RAM

    with open(file_path, encoding="utf8") as file:
        for line in file:
            m = matcher.match(line)
            if m:
                return m.group(1)
        else:
            return "-Unknown Vendor-"


def ipbytes_to_ipstr(ip: bytes) -> str:
    return socket.inet_ntoa(ip)


def netmaskbytes_to_prefixlen(netmask: bytes) -> int:
    bits = 0
    valid_maskbytes = {255<<8-bits & 255: bits for bits in range(9)}

    for b in netmask:
        if b not in valid_maskbytes:
            raise ValueError("Invalid subnet mask")

        if not b:
            break

        bits += valid_maskbytes[b]

    return bits
