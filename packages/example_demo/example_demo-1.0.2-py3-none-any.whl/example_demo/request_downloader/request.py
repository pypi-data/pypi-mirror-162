# -*- coding: UTF-8 -*-
import requests
import fabric
import ftplib
import traceback
import time
import cchardet
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from example_demo.monitor.log import log
import example_demo.commons.common_fun as common
import example_demo.setting as setting
from example_demo.request_downloader.response import Response


# 屏蔽warning信息
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Request(object):
    session = None
    user_agent_pool = None
    proxies_pool = None

    local_filepath = None
    oss_handler = None

    __REQUEST_ATTRS__ = {
        # 'method', 'url', 必须传递 不加入**kwargs中
        "params",
        "data",
        "headers",
        "cookies",
        "files",
        "auth",
        "timeout",
        "allow_redirects",
        "proxies",
        "hooks",
        "stream",
        "verify",
        "cert",
        "json",
    }

    DEFAULT_KEY_VALUE = dict(
        url="",
        retry_times=0,
        priority=300,
        parser_name=None,
        callback=None,
        filter_repeat=True,
        auto_request=True,
        request_sync=False,
        random_user_agent=True,
        download_midware=None,
        is_abandoned=False,

    )

    def __init__(
        self,
        url="",
        retry_times=0,
        priority=300,
        parser_name=None,
        callback=None,
        filter_repeat=True,
        auto_request=True,
        request_sync=False,
        random_user_agent=True,
        download_midware=None,
        is_abandoned=False,
        **kwargs,
    ):
        """
        @summary: Request参数
        ---------
        框架参数
        @param url: 待抓取url
        @param retry_times: 当前重试次数
        @param priority: 优先级 越小越优先 默认300
        @param parser_name: 回调函数所在的类名 默认为当前类
        @param callback: 回调函数 可以是函数 也可是函数名（如想跨类回调时，parser_name指定那个类名，callback指定那个类想回调的方法名即可）
        @param filter_repeat: 是否需要去重 (True/False) 当setting中的REQUEST_FILTER_ENABLE设置为True时该参数生效 默认True
        @param auto_request: 是否需要自动请求下载网页 默认是。设置为False时返回的response为空，需要自己去请求网页
        @param request_sync: 是否同步请求下载网页，默认异步。如果该请求url过期时间快，可设置为True，相当于yield的reqeust会立即响应，而不是去排队
        @param random_user_agent: 是否随机User-Agent (True/False) 当setting中的RANDOM_HEADERS设置为True时该参数生效 默认True
        @param download_midware: 下载中间件。默认为parser中的download_midware
        @param is_abandoned: 当发生异常时是否放弃重试 True/False. 默认False
        --
        以下参数与requests参数使用方式一致
        @param method: 请求方式，如POST或GET，默认根据data值是否为空来判断
        @param params: 请求参数
        @param data: 请求body
        @param json: 请求json字符串，同 json.dumps(data)
        @param headers:
        @param cookies: 字典 或 CookieJar 对象
        @param files:
        @param auth:
        @param timeout: (浮点或元组)等待服务器数据的超时限制，是一个浮点数，或是一个(connect timeout, read timeout) 元组
        @param allow_redirects : Boolean. True 表示允许跟踪 POST/PUT/DELETE 方法的重定向
        @param proxies: 代理 {"http":"http://xxx", "https":"https://xxx"}
        @param verify: 为 True 时将会验证 SSL 证书
        @param stream: 如果为 False，将会立即下载响应内容
        @param cert:
        --
        @param **kwargs: 其他值: 如 Request(item=item) 则item可直接用 request.item 取出
        ---------
        @result:
        """

        self.url = url
        self.retry_times = retry_times
        self.priority = priority
        self.parser_name = parser_name
        self.callback = callback
        self.filter_repeat = filter_repeat
        self.auto_request = auto_request
        self.request_sync = request_sync
        self.random_user_agent = random_user_agent
        self.download_midware = download_midware
        self.is_abandoned = is_abandoned

        self.requests_kwargs = {}
        for key, value in kwargs.items():
            if key in self.__class__.__REQUEST_ATTRS__:  # 取requests参数
                self.requests_kwargs[key] = value

            self.__dict__[key] = value

    def __repr__(self):
        try:
            return "<Request {}>".format(self.url)
        except:
            return "<Request {}>".format(str(self.to_dict)[:40])

    def __setattr__(self, key, value):
        """
        针对 request.xxx = xxx 的形式，更新reqeust及内部参数值
        @param key:
        @param value:
        @return:
        """
        self.__dict__[key] = value

        if key in self.__class__.__REQUEST_ATTRS__:
            self.requests_kwargs[key] = value

    def __lt__(self, other):
        return self.priority < other.priority

    # @property
    # def _session(self):
    #     use_session = (
    #         setting.USE_SESSION if self.use_session is None else self.use_session
    #     )  # self.use_session 优先级高
    #     if use_session and not self.__class__.session:
    #         self.__class__.session = requests.Session()
    #         # pool_connections – 缓存的 urllib3 连接池个数  pool_maxsize – 连接池中保存的最大连接数
    #         http_adapter = HTTPAdapter(pool_connections=1000, pool_maxsize=1000)
    #         # 任何使用该session会话的 HTTP 请求，只要其 URL 是以给定的前缀开头，该传输适配器就会被使用到。
    #         self.__class__.session.mount("http", http_adapter)
    #
    #     return self.__class__.session



    # @property
    # def _proxies_pool(self):
    #     if not self.__class__.proxies_pool:
    #         self.__class__.proxies_pool = ProxyPool()
    #
    #     return self.__class__.proxies_pool

    @property
    def to_dict(self):
        request_dict = {}

        self.callback = (
            getattr(self.callback, "__name__")
            if callable(self.callback)
            else self.callback
        )
        self.download_midware = (
            getattr(self.download_midware, "__name__")
            if callable(self.download_midware)
            else self.download_midware
        )

        for key, value in self.__dict__.items():
            if (
                key in self.__class__.DEFAULT_KEY_VALUE
                and self.__class__.DEFAULT_KEY_VALUE.get(key) == value
                or key == "requests_kwargs"
            ):
                continue

            if key in self.__class__.__REQUEST_ATTRS__:
                if not isinstance(
                    value, (bytes, bool, float, int, str, tuple, list, dict)
                ):
                    value = common.dumps_obj(value)
            else:
                if not isinstance(value, (bytes, bool, float, int, str)):
                    value = common.dumps_obj(value)

            request_dict[key] = value

        return request_dict

    @property
    def callback_name(self):
        return (
            getattr(self.callback, "__name__")
            if callable(self.callback)
            else self.callback
        )

    def get_response(self, save_cached=False):
        """
        获取带有selector功能的response
        @param save_cached: 保存缓存 方便调试时不用每次都重新下载
        @return:
        """
        # 设置超时默认时间
        self.requests_kwargs.setdefault(
            "timeout", setting.SOURCE_REQUEST_TIMEOUT
        )  # connect=22 read=22

        # 设置stream
        # 默认情况下，当你进行网络请求后，响应体会立即被下载。你可以通过 stream 参数覆盖这个行为，推迟下载响应体直到访问 Response.content 属性。此时仅有响应头被下载下来了。缺点： stream 设为 True，Requests 无法将连接释放回连接池，除非你 消耗了所有的数据，或者调用了 Response.close。 这样会带来连接效率低下的问题。
        self.requests_kwargs.setdefault("stream", True)

        # 关闭证书验证
        self.requests_kwargs.setdefault("verify", False)

        # 设置请求方法
        method = self.__dict__.get("method")
        if not method:
            if "data" in self.requests_kwargs or "json" in self.requests_kwargs:
                method = "POST"
            else:
                method = "GET"

        # 随机user—agent
        headers = self.requests_kwargs.get("headers", {})
        # if setting.SOURCE_NEED_UA:
        #     if "user-agent" in headers or "User-Agent" in headers:
        #         self.requests_kwargs.setdefault(
        #             "headers", {"User-Agent": setting.SOURCE_DEFAULT_UA}
        #         )
            # if "user-agent" not in headers and "User-Agent" not in headers:
            #
            #     ua = self.__class__.user_agent_pool.get(setting.USER_AGENT_TYPE)
            #
            #     if self.random_user_agent and setting.RANDOM_HEADERS:
            #         headers.update({"User-Agent": ua})
            #         self.requests_kwargs.update(headers=headers)
            # else:
            #     self.requests_kwargs.setdefault(
            #         "headers", {"User-Agent": setting.DEFAULT_USERAGENT}
            #     )

        # 代理
        # proxies = self.requests_kwargs.get("proxies", -1)
        # if proxies == -1 and setting.PROXY_ENABLE and setting.PROXY_EXTRACT_API:
        #     while True:
        #         proxies = self._proxies_pool.get()
        #         if proxies:
        #             self.requests_kwargs.update(proxies=proxies)
        #             break
        #         else:
        #             log.debug("暂无可用代理 ...")

        log.debug(
            """
                -------------- %srequest for ----------------
                url  = %s
                method = %s
                body = %s
                """
            % (
                ""
                if not self.parser_name
                else "%s.%s "
                % (
                    self.parser_name,
                    (
                        self.callback
                        and callable(self.callback)
                        and getattr(self.callback, "__name__")
                        or self.callback
                    )
                    or "parse",
                ),
                self.url,
                method,
                self.requests_kwargs,
            )
        )

        # def hooks(response, *args, **kwargs):
        #     print(response.url)
        #
        # self.requests_kwargs.update(hooks={'response': hooks})

        # use_session = (
        #     setting.USE_SESSION if self.use_session is None else self.use_session
        # )  # self.use_session 优先级高
        #
        #
        # if use_session:
        #     response = self._session.request(method, self.url, **self.requests_kwargs)
        #     response = Response(response)
        # else:
        response = requests.request(method, self.url, **self.requests_kwargs)
        response = Response(response)

        # 暂时不开
        # if save_cached:
        #     self.save_cached(response, expire_time=self.__class__.cached_expire_time)

        return response

    def proxies(self):
        """

        Returns: {"https": "https://ip:port", "http": "http://ip:port"}

        """
        return self.requests_kwargs.get("proxies")

    def proxy(self):
        """

        Returns: ip:port

        """
        proxies = self.proxies()
        if proxies:
            return proxies.get("http", "").strip("http://") or proxies.get(
                "https", ""
            ).strip("https://")

    def user_agent(self):
        headers = self.requests_kwargs.get("headers")
        if headers:
            return headers.get("user_agent") or headers.get("User-Agent")

    @property
    def fingerprint(self):
        """
        request唯一表识
        @return:
        """
        url = self.__dict__.get("url", "")
        # url 归一化
        url = common.canonicalize_url(url)
        args = [url]

        for arg in ["params", "data", "files", "auth", "cert", "json"]:
            if self.requests_kwargs.get(arg):
                args.append(self.requests_kwargs.get(arg))

        return common.get_md5(*args)



    @classmethod
    def from_dict(cls, request_dict):
        for key, value in request_dict.items():
            if isinstance(value, bytes):  # 反序列化 如item
                request_dict[key] = common.loads_obj(value)

        return cls(**request_dict)

    def copy(self):
        return self.__class__.from_dict(self.to_dict)
