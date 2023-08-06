import datetime
import uuid
import socket
import getpass

def new_uuid(prefix=None):
    u''' 生成前缀为 prefix 的唯一标识 '''
    if prefix:
        return "%s-%s" % (prefix, uuid.uuid1())
    return "%s" % (uuid.uuid1())

def get_hostname():
    u''' 返回主机名称 '''
    return socket.gethostname()


def get_user():
    return getpass.getuser()

def _now():
    return datetime.datetime.now().timestamp()

def get_ip():
    u''' 返回机器的ip地址 '''
    return socket.gethostbyname(socket.gethostname())

def _from_timestamp(t):
    if t is None:
        return None
    if isinstance(t, str):
        t = float(t)
    return datetime.datetime.fromtimestamp(t)

class objectview(object):
    u'''
    让dict可以通过对象的attr的方式访问。
    '''
    def __init__(self, d):
        self.__dict__ = d
