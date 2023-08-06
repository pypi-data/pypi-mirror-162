# -*- coding: utf-8 -*-
import attr
from datetime import datetime, timedelta

def remove_prefix(text, prefix):
    ''' 删除前缀(如果存在) '''
    return text[len(prefix):] if prefix and text.startswith(prefix) else text


class TaskState(object):
    UNKNOWN = "unknown"
    SUBMIT = "submit"
    RUNNING = "running"
    FINISH = "finish"
    FAIL = "fail"
    RETRY = "retry"

    @staticmethod
    def is_finished(s):
        return s == TaskState.FINISH or s == TaskState.FAIL

def _from_timestamp(t):
    if t is None:
        return None
    if isinstance(t, str):
        t = float(t)
    return datetime.fromtimestamp(t)


def _invalid_timestamp():
    return datetime(1999, 1, 1)


@attr.s
class AgentState(object):
    id = attr.ib()
    pid = attr.ib("")
    uptime = attr.ib(_invalid_timestamp())
    downtime = attr.ib(_invalid_timestamp())
    timestamp = attr.ib(_invalid_timestamp())
    wd = attr.ib("")
    mem_private = attr.ib(0.0)
    cpu_percent = attr.ib(0.0)
    num_children = attr.ib(0)

    @staticmethod
    def load(redis, id):
        s = AgentState(id)
        map = redis.hgetall(id)
        if not map:
            return s
        map = {k.decode(): v.decode() for k, v in map.items()}
        s.uptime = _from_timestamp(map.get('uptime'))
        s.ip = map.get('ip')
        s.timestamp = _from_timestamp(map.get('timestamp'))
        s.downtime = _from_timestamp(map.get('downtime'))
        s.mem_private = float(map.get('mem_private') or 0.)
        s.cpu_percent = float(map.get('cpu_percent') or 0.)
        s.num_children = int(map.get('num_children') or 0)
        s.wd = map.get('wd')
        s.pid = map.get('pid')
        return s

@attr.s
class MachineState(object):
    id = attr.ib()
    ip = attr.ib(None)
    name = attr.ib(None)
    uptime = attr.ib(_invalid_timestamp())
    mem = attr.ib(0.0)
    mem_usage = attr.ib(0.0)
    cpu = attr.ib(0)
    cpu_usage = attr.ib(0.0)
    num_cores = attr.ib(0)
    timestamp = attr.ib(_invalid_timestamp())

    @staticmethod
    def load(redis, id):
        ms = MachineState(id)
        map = redis.hgetall(id)
        if not map:
            return ms
        map = {k.decode(): v.decode() for k, v in map.items()}
        ms.name = map.get('name')
        ms.ip = map.get('ip')
        ms.mem = float(map.get('mem') or 0.)
        ms.mem_usage = float(map.get('mem_usage') or 0.0)
        ms.cpu_usage = float(map.get('cpu_usage') or 0.0)
        ms.num_cores = int(map.get('num_cores') or 0)
        ms.timestamp = _from_timestamp(map.get('timestamp'))
        return ms

class RedisObject(object):

    def __init__(self, redis, id):
        self.redis = redis
        self._id = id

class Task(RedisObject):
    PREFIX = 't'

    def __init__(self, redis, id):
        self.redis = redis
        self._id = id

    def destroy(self):
        self.redis.delete(self._id)

class Pool(RedisObject):
    PREFIX = 'j'

    def __init__(self, redis, id):
        self.redis = redis
        self._id = id
        self._TASKS_KEY = f'{self._id}:tasks'
        self._PENDING_KEY = f'{self._id}:pending'
        self._RUNNING_KEY = f'{self._id}:running'
        self._FINISH_KEY = f'{self._id}:finish'
        self._FAIL_KEY = f'{self._id}:fail'

    @property
    def task_ids(self):
        task_ids = self.redis.lrange(self._TASKS_KEY, 0, -1)
        for task_id in task_ids:
            yield task_id.decode()

    @property
    def tasks(self):
        for task_id in self.task_ids:
            yield Task(self.redis, task_id)

    def destroy(self):
        with self.redis.pipeline() as tx:
            tx.multi()
            for task in self.tasks:
                task.destroy()
            tx.delete(self._PENDING_KEY)
            tx.delete(self._RUNNING_KEY)
            tx.delete(self._FINISH_KEY)
            tx.delete(self._FAIL_KEY)
            tx.delete(self._TASKS_KEY)
            tx.delete(self._id)
            tx.execute()

@attr.s
class PoolState(object):
    id = attr.ib()
    create_time = attr.ib(_invalid_timestamp())
    parallels = attr.ib(0)
    total = attr.ib(0)
    pending = attr.ib(0)
    finished = attr.ib(0)
    running = attr.ib(0)
    failed = attr.ib(0)
    cost = attr.ib(timedelta())
    eta = attr.ib(timedelta())
    running_tasks = attr.ib([])

    def get_tasks(self, redis):
        tasks = redis.lrange(f'{self.id}:tasks', 0, -1)
        return [task.decode() for task in tasks]

    @staticmethod
    def load(redis, id):
        s = PoolState(id)
        map = redis.hgetall(id)
        if not map:
            return s
        map = {k.decode(): v.decode() for k, v in map.items()}
        s.create_time = _from_timestamp(map.get('create_time'))
        s.parallels = int(map.get('parallels') or 0)
        s.total = int(map.get('num_tasks') or 0)
        s.finished = redis.llen(f'{id}:finish')
        s.pending = redis.llen(f'{id}:pending')
        s.running = redis.llen(f'{id}:running')
        s.running_tasks = [t.decode() for t in redis.lrange(f'{id}:running', 0, -1)]
        s.failed = redis.llen(f'{id}:fail')
        s.cost = datetime.now() - s.create_time
        if s.finished + s.failed != 0:
            s.eta = s.cost / (s.finished + s.failed) * (s.total - s.finished - s.failed)
        else:
            s.eta = timedelta()
        return s
@attr.s
class ScriptInfo(object):
    id = attr.ib()
    name = attr.ib('')
    state = attr.ib(TaskState.SUBMIT)
    start_time = attr.ib(None)
    cost = attr.ib(timedelta())
    agent = attr.ib(None)
    mem_private = attr.ib(0.0)
    cpu_percent = attr.ib(0.0)
    create_time = attr.ib(None)
    exit_time = attr.ib(None)
    timestamp = attr.ib(_invalid_timestamp())
    wd = attr.ib('')
    cmd = attr.ib('')
    state_msg = attr.ib('')
    pid = attr.ib('')
    current = attr.ib('')
    cs_queue = attr.ib(0)
    cs_total = attr.ib(0)
    cs_running = attr.ib(0)
    cs_cost = attr.ib(0)
    cs_estimate = attr.ib(0)
@attr.s
class ProcessState(object):
    id = attr.ib()
    pid = attr.ib("")
    agent = attr.ib("")
    cmd = attr.ib("")
    start_time = attr.ib(_invalid_timestamp())
    mem_private = attr.ib(0.0)
    cpu_percent = attr.ib(0.0)
    num_children = attr.ib(0)
    state = attr.ib(TaskState.UNKNOWN)
    wd = attr.ib("")
    timestamp = attr.ib(_invalid_timestamp())
    finish = attr.ib(0)
    fail = attr.ib(0)
    running = attr.ib(0)

    @staticmethod
    def load(redis, id):
        s = ProcessState(id)
        map = redis.hgetall(id)
        if not map:
            return s
        map = {k.decode(): v.decode() for k, v in map.items()}
        s.create_time = _from_timestamp(map.get('create_time'))
        s.agent = map.get('agent')
        s.pid = map.get('pid')
        args = redis.lrange(f'{id}:args', 0, -1)
        s.cmd = ' '.join([arg.decode() for arg in args])
        s.timestamp = _from_timestamp(map.get('timestamp'))
        s.start_time = _from_timestamp(map.get('start_time'))
        s.mem_private = float(map.get('mem_private') or 0)
        s.cpu_percent = float(map.get('cpu_percent') or 0)
        s.num_children = int(map.get('num_children') or 0)
        s.running = int(map.get('running') or 0)
        s.finish = int(map.get('finish') or 0)
        s.fail = int(map.get('fail') or 0)
        s.wd = map.get('wd')
        s.exit_time = _from_timestamp(map.get('exit_time'))
        s.state = map.get('state')
        s.state_msg = map.get('state_msg')
        return s




# 清理脚本相关的所有状态
class Script(RedisObject):
    PREFIX = 's'

    def __init__(self, redis, id, user, name):
        self.redis = redis
        self.user = user
        self.name = name
        self.id = id
        self._POOLS_KEY = f'{self.id}:pools'
        self._USER_POOLS_KEY = f'u-{self.user}:pools'

    @classmethod
    def from_name(cls, redis, user, name):
        id = Script.make_id(user, name)
        return Script(redis, id, user, name)

    @classmethod
    def from_id(cls, redis, id):
        p, u, n = id.split('-', 2)
        assert p == cls.PREFIX
        return Script(redis, id, u, n)

    @classmethod
    def make_id(cls, user, name):
        return f'{cls.PREFIX}-{user}-{name}'

    @property
    def agent(self):
        agent = self.redis.hget(self.id, 'agent')
        return agent.decode() if agent else None

    @property
    def pools(self):
        items = self.redis.smembers(self._POOLS_KEY)
        return {Pool(self.redis, item.decode()) for item in items}

    def clean_pools(self):
        for pool in self.pools:
            pool.destroy()
            self.redis.srem(self._POOLS_KEY, pool._id)
            self.redis.srem(self._USER_POOLS_KEY, pool._id)

    def destroy(self):
        self.clean_pools()
        self.redis.delete(self.id)

    def pool_state(self):
        items = [item.decode() for item in self.redis.smembers(self._POOLS_KEY)]
        pools = [PoolState.load(self.redis, pool) for pool in items]
        ps = PoolState(''.join(items))
        ps.running = sum([pool.running for pool in pools])
        ps.pending = sum([pool.pending for pool in pools])
        ps.parallels = sum([pool.parallels for pool in pools])
        ps.failed = sum([pool.failed for pool in pools])
        ps.finished = sum([pool.finished for pool in pools])
        ps.total = sum([pool.total for pool in pools])
        if pools:
            ps.cost = max([pool.cost for pool in pools])
            ps.eta = max([pool.eta for pool in pools])
        return ps

    @property
    def state(self):
        map = self.redis.hgetall(self.id)
        s = ScriptInfo(self.id)
        if map:
            map = {k.decode(): v.decode() for k, v in map.items()}
            state = map.get('state')
            s.name = map.get('name')
            if not s.name:
                s.name = remove_prefix(self.id, f's-{self.user}-')
            s.state = map.get('state')
            s.create_time = _from_timestamp(map.get('submit_time'))
            s.agent = map.get('agent')
            args = self.redis.lrange(f'{self.id}:args', 0, -1)
            s.cmd = ' '.join([arg.decode() for arg in args])
            s.timestamp = _from_timestamp(map.get('timestamp'))
            if state == TaskState.RUNNING:
                s.pid = map.get('pid')
                s.start_time = _from_timestamp(map.get('start_time'))
                s.mem_private = float(map.get('mem_private') or 0)
                s.cpu_percent = float(map.get('cpu_percent') or 0)
                if s.start_time:
                    s.cost = datetime.now() - s.start_time
                s.wd = map.get('wd')
            elif state == TaskState.FINISH or state == TaskState.FAIL:
                s.start_time = _from_timestamp(map.get('start_time'))
                s.exit_time = _from_timestamp(map.get('exit_time'))
                s.state_msg = map.get('state_msg')
                if s.exit_time and s.start_time:
                    s.cost = s.exit_time - s.start_time
        else:
            s.name = self.name
            s.state = TaskState.UNKNOWN

        pstate = self.pool_state()
        s.cs_queue = pstate.pending
        s.cs_running = pstate.running
        s.cs_total = pstate.total
        s.cs_cost = pstate.cost
        s.cs_estimate = pstate.eta
        s.current = s.id
        return s


@attr.s
class TaskObject(object):
    u''' 读取redis的task任务数据 '''
    id = attr.ib()
    pid = attr.ib("")
    worker = attr.ib("")
    create_time = attr.ib(_invalid_timestamp())
    start_time = attr.ib(_invalid_timestamp())
    finish_time = attr.ib(_invalid_timestamp())
    timestamp = attr.ib(_invalid_timestamp())
    state = attr.ib(TaskState.UNKNOWN)
    job_id = attr.ib('')
    elapse = attr.ib(timedelta())
    label = attr.ib("")
    script_id = attr.ib("")
    call_depth = attr.ib(1)
    # spec
    mem_private = attr.ib(0.0)
    cpu_percent = attr.ib(0.0)
    num_children = attr.ib(0)

    @staticmethod
    def load(redis, id):
        s = TaskObject(id)
        keys = [
            "job_id", "create_time", "worker", "label", "script_id", "call_depth", "state", "timestamp", "start_time",
            "finish_time", "pid", "mem_private", "cpu_percent", "num_children"
        ]
        values = redis.hmget(id, keys)
        if not values:
            return s
        map = {k: v.decode() for k, v in zip(keys, values) if v is not None}
        s.create_time = _from_timestamp(map.get('create_time'))
        s.worker = map.get('worker')
        s.timestamp = _from_timestamp(map.get('timestamp'))
        s.start_time = _from_timestamp(map.get('start_time'))
        s.finish_time = _from_timestamp(map.get('finish_time'))
        s.state = map.get('state')
        s.job_id = map.get('job_id')
        s.label = map.get('label')
        s.script_id = map.get('script_id')
        s.call_depth = map.get('call_depth')
        s.pid = map.get('pid')
        s.mem_private = float(map.get('mem_private') or 0)
        s.cpu_percent = float(map.get('cpu_percent') or 0)
        s.num_children = int(map.get('num_children') or 0)
        if s.state == TaskState.RUNNING:
            s.elapse = datetime.now() - s.start_time
        elif s.state == TaskState.FINISH:
            if s.finish_time:
                s.elapse = s.finish_time - s.start_time
        elif s.state == TaskState.FAIL:
            if s.finish_time:
                s.elapse = s.finish_time - s.start_time
        return s
