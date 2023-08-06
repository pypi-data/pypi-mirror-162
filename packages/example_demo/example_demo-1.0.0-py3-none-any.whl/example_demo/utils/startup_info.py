from collections import namedtuple
import os


class StartupInfo(
        namedtuple(
            "StartupInfo",
            "work_dir,jupyter_server,jupyter_port,custom_zone,system_zone,jupyter_samples_server,jupyter_samples_path")
):

    @staticmethod
    def read_from_redis(redis, user):
        uid = f'u-{user}'
        sys_options = redis.hgetall('::options')
        if not sys_options:
            raise Exception("Internal Error.")
        user_options = redis.hgetall(uid)
        if not user_options:
            raise Exception(f"Invalid user: {user}")

        cz = sys_options[b'custom_zone'].decode()
        sz = sys_options[b'system_zone'].decode()
        work_dir = os.path.join(cz, user)
        jupyter_port = user_options[b'jupyter_port'].decode()
        jupyter_server = user_options.get(b'jupyter_server', None)
        if jupyter_server:
            jupyter_server = jupyter_server.decode()
        jupyter_samples_server = sys_options.get(b'jupyter_server', None)
        jupyter_samples_server = jupyter_samples_server and jupyter_samples_server.decode() or None
        jupyter_samples_path = sys_options.get(b'jupyter_samples_path', None)
        jupyter_samples_path = jupyter_samples_path and jupyter_samples_path.decode() or None
        return StartupInfo(work_dir, jupyter_server, jupyter_port, cz, sz, jupyter_samples_server, jupyter_samples_path)

    def set_jupyter_server(self, n):
        items = list(self)
        items[1] = n
        return StartupInfo(*items)
