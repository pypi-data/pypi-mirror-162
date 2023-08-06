import random
from typing import Any, List, Optional, Tuple, Callable, Dict, Union
import datetime
import cchardet
import traceback
import os
from requests.auth import HTTPBasicAuth
import requests
import tenacity

from example_demo.request_downloader.download_base import BaseHook
from example_demo.exceptions import OnedatautilConfigException

from example_demo.request_downloader.downloaders import agents

class HttpHook(BaseHook):
    """
    Interact with HTTP servers.

    :param method: the API method to be called

    :param auth_type: The auth type for the service
    """

    def __init__(
            self,
            method: str = 'GET',
            auth_type: Any = HTTPBasicAuth,
            request_info=None,
    ) -> None:
        super().__init__()
        if request_info is None:
            request_info = {}
        self.method = method.upper()
        self.base_url: str = ""
        self._retry_obj: Callable[..., Any]
        self.auth_type: Any = auth_type
        self.request_info = request_info

    # headers may be passed through directly or in the "extra" field in the connection
    # definition
    def get_conn(self, headers: Optional[Dict[Any, Any]] = None) -> requests.Session:
        """
        Returns http session for use with requests

        :param headers: additional headers to be passed through as a dictionary
        """
        session = requests.Session()

        if self.request_info:
            # conn = self.get_connection()
            self.base_url = self.request_info.get("url")
            request_auth_name = self.request_info.get("request_auth_name")
            request_auth_password = self.request_info.get("request_auth_password")
            if request_auth_name and request_auth_password:
                session.auth = self.auth_type(request_auth_name, request_auth_password)
            # if conn.extra:
            #     try:
            #         session.headers.update(conn.extra_dejson)
            #     except TypeError:
            #         print('')
            #         self.log.warning('Connection to %s has invalid extra field.', conn.host)
        if headers:
            session.headers.update(headers)

        return session

    def run(
            self,
            endpoint: Optional[str] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            headers: Optional[Dict[str, Any]] = None,
            extra_options: Optional[Dict[str, Any]] = None,
            **request_kwargs: Any,
    ) -> Any:
        r"""
        Performs the request

        :param endpoint: the endpoint to be called i.e. resource/v1/query?
        :param data: payload to be uploaded or request parameters
        :param headers: additional headers to be passed through as a dictionary
        :param extra_options: additional options to be used when executing the request
            i.e. {'check_response': False} to avoid checking raising exceptions on non
            2XX or 3XX status codes
        :param request_kwargs: Additional kwargs to pass when creating a request.
            For example, ``run(json=obj)`` is passed as ``requests.Request(json=obj)``
        """
        extra_options = extra_options or {}

        session = self.get_conn(headers)

        url = self.url_from_endpoint(endpoint)

        if self.method == 'GET':
            # GET uses params
            req = requests.Request(self.method, url, params=data, headers=headers, **request_kwargs)
        elif self.method == 'HEAD':
            # HEAD doesn't use params
            req = requests.Request(self.method, url, headers=headers, **request_kwargs)
        else:
            # Others use data
            req = requests.Request(self.method, url, data=data, headers=headers, **request_kwargs)

        prepped_request = session.prepare_request(req)
        # self.log.info("Sending '%s' to url: %s", self.method, url)
        return self.run_and_check(session, prepped_request, extra_options)

    def check_response(self, response: requests.Response) -> None:
        """
        Checks the status code and raise an AirflowException exception on non 2XX or 3XX
        status codes

        :param response: A requests response object
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("HTTP error: %s", response.reason)
            print(response.text)

    def run_and_check(
            self,
            session: requests.Session,
            prepped_request: requests.PreparedRequest,
            extra_options: Dict[Any, Any],
    ) -> Any:
        """
        Grabs extra options like timeout and actually runs the request,
        checking for the result

        :param session: the session to be used to execute the request
        :param prepped_request: the prepared request generated in run()
        :param extra_options: additional options to be used when executing the request
            i.e. ``{'check_response': False}`` to avoid checking raising exceptions on non 2XX
            or 3XX status codes
        """
        extra_options = extra_options or {}

        settings = session.merge_environment_settings(
            prepped_request.url,
            proxies=extra_options.get("proxies", {}),
            stream=extra_options.get("stream", False),
            verify=extra_options.get("verify"),
            cert=extra_options.get("cert"),
        )

        # Send the request.
        send_kwargs: Dict[str, Any] = {
            "timeout": extra_options.get("timeout"),
            "allow_redirects": extra_options.get("allow_redirects", True),
        }
        send_kwargs.update(settings)

        try:
            response = session.send(prepped_request, **send_kwargs)

            if extra_options.get('check_response', True):
                self.check_response(response)
            return response

        except requests.exceptions.ConnectionError as ex:
            print('%s Tenacity will retry to execute the operation', ex)
            # self.log.warning('%s Tenacity will retry to execute the operation', ex)
            raise ex

    def run_with_advanced_retry(self, _retry_args: Dict[Any, Any], *args: Any, **kwargs: Any) -> Any:
        """
        Runs Hook.run() with a Tenacity decorator attached to it. This is useful for
        connectors which might be disturbed by intermittent issues and should not
        instantly fail.

        :param _retry_args: Arguments which define the retry behaviour.
            See Tenacity documentation at https://github.com/jd/tenacity


        .. code-block:: python

            hook = HttpHook(http_conn_id="my_conn", method="GET")
            retry_args = dict(
                wait=tenacity.wait_exponential(),
                stop=tenacity.stop_after_attempt(10),
                retry=requests.exceptions.ConnectionError,
            )
            hook.run_with_advanced_retry(endpoint="v1/test", _retry_args=retry_args)

        """
        self._retry_obj = tenacity.Retrying(**_retry_args)

        return self._retry_obj(self.run, *args, **kwargs)

    def url_from_endpoint(self, endpoint: Optional[str]) -> str:
        """Combine base url with endpoint"""
        if self.base_url and not self.base_url.endswith('/') and endpoint and not endpoint.startswith('/'):
            return self.base_url + '/' + endpoint
        return (self.base_url or '') + (endpoint or '')


class HTTPDownloader(HttpHook):
    def __init__(self, sour, *args, **kwargs):
        self.sour = sour

        request_info = self.init_request_info()

        self.get_request_method()
        kwargs['request_info'] = request_info

        super().__init__(*args, **kwargs)

    def get_request_method(self):
        request_type = self.sour.get("request_info")
        if request_type == 'api_get':
            self.method = "GET"
        elif request_type == 'api_post':
            self.method = "POST"

    def init_request_info(self):
        request_info = self.sour.get("request_info", {})
        if self.sour.get("request_auth_name") and self.sour.get("request_auth_password"):
            request_info["request_auth_name"] = self.sour.get("request_auth_name")
            request_info["request_auth_password"] = self.sour.get("request_auth_password")
        if not request_info.get("url") and self.sour.get("url"):
            request_info["url"] = self.sour.get("url")

        return request_info

    def downloader(self, need_content=True, binary=False):
        headers = {}
        if self.sour.get("request_need_ua"):
            headers["User-Agent"] = random.choice(agents)
        request_timeout = self.sour.get("request_timeout") or 10
        request_try_num = self.sour.get("request_try_num") or 3
        data = self.sour.get("url_params")
        res_content = None
        download_res = False
        extra_options = {
            "time_out": request_timeout,
            # "allow_redirects":  True,

        }
        for try_num in range(request_try_num):
            try:
                res = self.run(data=data, headers=headers, extra_options=extra_options)
                if res.status_code != 200:
                    continue
                if not need_content:
                    return res
                if binary:
                    res_content = res.content
                else:
                    encoding_type = cchardet.detect(res.content)["encoding"]
                    res_content = res.content.decode(encoding_type)
                download_res = True
                break
            except Exception as e:
                traceback.print_exc()
                print(f'request_download_fail,tru_num:{try_num}')
                continue
        return download_res, res_content