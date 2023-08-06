import itertools
import os
import platform
import socket


def get_logon_prefix():
    u''' 返回 jinde.local 中的 jinde '''
    return socket.getfqdn().split('.')[1]

_DOMAIN = "JINDE"
try:
    _DOMAIN = get_logon_prefix().upper()
except:  # pylint: disable=bare-except
    pass
_JD_SCRIPT_ID = "_JD_SCRIPT_ID"
# DPool的嵌套尝试
_JD_CALL_DEPTH = "_JD_CALL_DEPTH"
_HUB_URL = "_JD_HUB_URL"
_JD_CUSTOM_ZONE = "_JD_CUSTOM_ZONE"
_JD_SYSTEM_ZONE = "_JD_SYSTEM_ZONE"



def get_pid(prefix):
    u''' 返回主机名及进程标识，附加前缀 '''
    return "%s~%s~%s" % (prefix or 'U', platform.node(), os.getpid())


def _SCRIPT_ID():
    id = os.environ.get(_JD_SCRIPT_ID)
    if id is None:
        try:
            import __main__
            id = os.path.basename(__main__.__file__)
        except:  # pylint: disable=bare-except
            id = get_pid('script')
    return id


def _CALL_DEPTH():
    depth = os.environ.get(_JD_CALL_DEPTH)
    return 1 if depth is None else int(depth) + 1


__all__ = [
    "_JD_SCRIPT_ID", "_JD_CALL_DEPTH", "_HUB_URL", "_SCRIPT_ID", "_CALL_DEPTH", "_JD_CUSTOM_ZONE", "_JD_SYSTEM_ZONE",
    "_DOMAIN"
]
