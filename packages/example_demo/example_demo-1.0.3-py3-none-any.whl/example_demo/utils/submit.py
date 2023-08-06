import os
import yaml
import shutil
import logging as log
from example_demo.utils._constants import  _JD_CUSTOM_ZONE, _JD_SYSTEM_ZONE
from example_demo.utils.util_fun import new_uuid, get_user
from example_demo.mrjob.fs.local import LocalFilesystem
from example_demo.mrjob.setup import UploadDirManager
# from _constants import _JD_CUSTOM_ZONE, _JD_SYSTEM_ZONE
# from util_fun import new_uuid, get_user
# 用户的共享存储目录。
CUSTOM_ZONE_ROOT = r"\\192.168.2.34\quant\customzone"
# 公共存储目录。
DEFAULT_SYSTEM_ZONE = r"\\192.168.2.34\quant\systemzone"

# 工作目录名
JOB_DIR = "job"
# 作业清单文件
MANIFEST_FILE = 'manifest.yaml'
# 程序日志文件
STDOUT_FILE = 'stdout.txt'
INTERPRETER = 'python.exe'


class ManifestError(Exception):
    pass

class Manifest(object):
    u'''
    任务清单，以YAML格式描述。
    '''

    def __init__(self, options={}):
        self.name = ""
        self.description = ""
        self.author = ""
        self.files = list()
        self.py_files = list()
        self.refs = list()
        self.main = None
        self.args = []
        self.env = dict()
        self.parallels = 0
        self.timeout = 0
        self.retry_times = 0
        self.requires = dict()
        self.__dict__.update(options)

    @staticmethod
    def parse(s):
        return Manifest(yaml.safe_load(s))

    @staticmethod
    def load_from_file(file, encoding=None):
        for code in [encoding, 'utf8', 'gbk']:
            try:
                with open(file, 'r+', encoding=code) as f:
                    return Manifest(yaml.safe_load(f.read()))
            except UnicodeDecodeError:
                continue

    def __str__(self):
        return repr(self)

    def __repr__(self):

        def _dump_value(k, v):
            if isinstance(v, list) or isinstance(v, set):
                v = "\n".join("  - %s" % e for e in v)
                return "%s: \n%s" % (k, v)
            elif isinstance(v, dict):
                v = "\n".join("  %s: %s" % (k, v) for k, v in v.items())
                return "%s: \n%s" % (k, v)
            else:
                return "%s: %s" % (k, v)

        txt = "\n".join(_dump_value(k, v) for k, v in self.__dict__.items() if v)
        return txt

    def toyaml(self):
        return str(self)

    def save(self, file):
        with open(file, 'w+', encoding='utf8') as f:
            f.write(self.toyaml())


class Context(object):

    def __init__(self, manifest, custom_zone=None, system_zone=None, user=None):
        custom_zone = custom_zone or os.environ.get(_JD_CUSTOM_ZONE, None)
        system_zone = system_zone or os.environ.get(_JD_SYSTEM_ZONE, None)
        self._custom_zone = custom_zone or CUSTOM_ZONE_ROOT
        self.user = user or get_user()
        self.prefix = os.path.join(self._custom_zone, self.user, JOB_DIR)
        self.manifest = manifest
        self._system_zone = system_zone or DEFAULT_SYSTEM_ZONE
        self.fs = LocalFilesystem()

    @staticmethod
    def from_name(name, custom_zone=None, system_zone=None, user=None):
        ctx = Context(None, custom_zone=custom_zone, system_zone=system_zone, user=user)
        manifest_file = os.path.join(ctx.prefix, name, MANIFEST_FILE)
        if not ctx.fs.exists(manifest_file):
            raise ValueError("无效作业名称，未找到作业清单文件 %s" % manifest_file)
        ctx.manifest = Manifest.load_from_file(manifest_file)
        return ctx

    @property
    def name(self):
        return self.manifest.name

    # @property
    # def user_dir(self):
    #     return os.path.join(self.root, self.user)

    @property
    def wd_mirror(self):
        u''' 返回工作目录在共享存储中的位置。用户名+任务名 '''
        return os.path.join(self.prefix, self.name)

    @property
    def manifest_file(self):
        u''' 返回清单文件路径  '''
        return os.path.join(self.wd_mirror, MANIFEST_FILE)

    @property
    def custom_zone(self):
        return self._custom_zone

    @property
    def system_zone(self):
        return self._system_zone

    @property
    def stdout_path(self):
        return os.path.join(self.wd_mirror, STDOUT_FILE)

    @property
    def interpreter(self):
        return INTERPRETER


class Submit(Context):
    u'''
    提交作业相关资源的过程。
    '''

    def __init__(self, manifest, wd, local_manifest_file=None, **kwargs):
        super(Submit, self).__init__(manifest, **kwargs)
        self.wd = wd
        self._upload_mgr = UploadDirManager(self.wd_mirror)
        self.added_files = dict()
        self.local_manifest_file = local_manifest_file

    @staticmethod
    def from_manifest(manifest_file: str = MANIFEST_FILE, **kwargs):
        x = os.path.abspath(manifest_file)
        wd = os.path.dirname(x)
        manifest = Manifest.load_from_file(manifest_file)
        submit = Submit(manifest, wd, **kwargs)
        submit.add_file(manifest_file)
        return submit

    @staticmethod
    def make(main, name=None, files=[], **kwargs):
        x = os.path.abspath(main)
        wd = os.path.dirname(x)
        main = os.path.basename(main)
        name = name or main
        xfiles = [os.path.relpath(file, wd) for file in files]
        manifest = Manifest(options=dict(main=main, name=name, files=xfiles))
        manifest_file = os.path.join(wd, MANIFEST_FILE)
        manifest.save(manifest_file)
        manifest = Manifest.load_from_file(manifest_file)
        submit = Submit(manifest, wd, local_manifest_file=manifest_file, **kwargs)
        submit.add_file(manifest_file)
        return submit

    def abspath(self, file):
        return os.path.join(self.wd, file)

    def check_files(self):
        files = self.manifest.files + \
            self.manifest.py_files + [self.manifest.main]
        for file in files:
            abspath = self.abspath(file)
            if not self.fs.exists(abspath):
                raise ManifestError("no such file: %s" % file)
            self.added_files[abspath] = file

        for ref in self.manifest.refs:
            if not self.fs.exists(ref):
                raise ManifestError("no such ref: %s" % ref)

    def upload_files(self):
        for abspath, file in self.added_files.items():
            self._upload_mgr.add(abspath, file)

        self.fs.mkdir(self._upload_mgr.prefix)
        log.info('Copying other local files to %s', self._upload_mgr.prefix)
        for src_path, uri in self._upload_mgr.path_to_uri().items():
            log.debug('  %s -> %s', src_path, uri)
            self.fs.mkdir(os.path.dirname(uri))
            if os.path.isdir(src_path):
                if os.path.exists(uri):
                    shutil.rmtree(uri)
                shutil.copytree(src_path, uri)
            else:
                self.fs.put(src_path, uri)

    def write_submit_id(self):
        u''' 在目录中写入一个唯一的随机id，为后续同步作准备。'''
        submit_id = os.path.join(self._upload_mgr.prefix, 'submit_id.txt')
        with open(submit_id, 'w') as f:
            f.write(new_uuid())

    def add_file(self, file):
        x = os.path.abspath(file)
        self.added_files[x] = os.path.basename(file)

    def clean_temps(self):
        if self.local_manifest_file:
            os.unlink(self.local_manifest_file)
