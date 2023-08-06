import attr
import pickle


@attr.s(slots=True)
class ActorMessage(object):
    ''' 消息请求流水号(只有请求应答消息才有。) '''
    sn = attr.ib(default=0, validator=attr.validators.instance_of(int))
    ''' 消息发送方 '''
    sender = attr.ib(default="", validator=attr.validators.instance_of(str))
    ''' 消息接收方 '''
    target = attr.ib(default="", validator=attr.validators.instance_of(str))
    ''' 消息前缀，用户识别消息 '''
    prefix = attr.ib(default="", validator=attr.validators.instance_of(str))
    ''' 消息负载 '''
    payload = attr.ib(default=b'', validator=attr.validators.instance_of(type(b'')))

    def SerializeToString(self):
        data = {
            slot: getattr(self, slot) for slot in self.__slots__ if not slot.startswith('__') and hasattr(self, slot)  # pylint: disable=no-member
        }
        return pickle.dumps(data)

    def ParseFromString(self, s):
        data = pickle.loads(s)
        for k, v in data.items():
            setattr(self, k, v)
