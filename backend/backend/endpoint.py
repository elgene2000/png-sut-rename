import abc
import requests
import socket
import urllib3

from version import version
from typing import Any, Dict, List, Optional, Union
from environment import REQUEST_TIMEOUT, VERIFY_CERTS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class RequestEngine:
    def get(self, route: str, **kwargs):
        res = requests.get(
            self._build_route(route),
            headers=self._get_headers(),
            json=kwargs,
            verify=VERIFY_CERTS,
            timeout=REQUEST_TIMEOUT,
        )

        try:
            contents = res.json()
        except requests.exceptions.JSONDecodeError:
            contents = ""
        if res.status_code == 401:
            raise AuthorizationError(str(contents))
        elif res.status_code >= 400:
            raise RequestError(str(contents))
        return contents

    def post(
        self,
        route: str,
        data: Dict = None,
        files: Any = None,
        return_response: bool = False,
        **_,
    ) -> Union[List, Dict, requests.Response]:
        if files:
            res = requests.post(
                self._build_route(route),
                headers=self._get_headers(),
                data=data,
                files=files,
                verify=VERIFY_CERTS,
                timeout=REQUEST_TIMEOUT,
            )
        else:
            res = requests.post(
                self._build_route(route),
                headers=self._get_headers(),
                json=data,
                verify=VERIFY_CERTS,
                timeout=REQUEST_TIMEOUT,
            )
        try:
            contents = res.json()
        except requests.exceptions.JSONDecodeError:
            contents = ""
        if res.status_code == 401:
            raise AuthorizationError(str(contents))
        elif res.status_code >= 400 and return_response is not True:
            raise RequestError(str(contents))
        return contents if return_response is not True else res

    def put(
        self, route: str, data: Dict = None, return_response: bool = False, **_
    ) -> Union[List, Dict, requests.Response]:
        res = requests.put(
            self._build_route(route),
            headers=self._get_headers(),
            json=data,
            verify=VERIFY_CERTS,
            timeout=REQUEST_TIMEOUT,
        )
        try:
            contents = res.json()
        except requests.exceptions.JSONDecodeError:
            contents = ""
        if res.status_code == 401:
            raise AuthorizationError(str(contents))
        elif res.status_code >= 400 and return_response is not True:
            raise RequestError(str(contents))
        return contents if return_response is not True else res

    def delete(
        self, route: str, data: Dict = None, return_response: bool = False, **_
    ) -> Union[List, Dict, requests.Response]:
        res = requests.delete(
            self._build_route(route),
            headers=self._get_headers(),
            json=data,
            verify=VERIFY_CERTS,
            timeout=REQUEST_TIMEOUT,
        )
        try:
            contents = res.json()
        except requests.exceptions.JSONDecodeError:
            contents = ""
        if res.status_code == 401:
            raise AuthorizationError(str(contents))
        elif res.status_code >= 400 and return_response is not True:
            raise RequestError(str(contents))
        return contents if return_response is not True else res

    def _get_headers(self) -> Dict:
        """Ensure we get latest values for conductor
        secrets in case they are updated in environment after initial import.

        Returns:
            Dict: The headers to use for API request.
        """
        from at_scale_python_api.environment import (
            get_email,
            get_secret,
        )

        headers = {
            "Package-Version": version,
            "Requester-Origin": socket.gethostname(),
            "Authorization": (
                (get_email() + ":" + get_secret()) if get_email() else get_secret()
            ),
        }
        return headers

    def _build_route(self, route: str) -> str:
        from at_scale_python_api.environment import get_url

        return f"{get_url()}/{route}"


class Endpoint(abc.ABC):
    route = ""
    model = None
    schema = None

    def __init__(self):
        self.requester = RequestEngine()

    def _clear_unused(self, data: Dict) -> Dict:
        used_data = {}
        for key, value in data.items():
            if value is not None:
                used_data[key] = value
        return used_data

    def get(self, identifier=None, **kwargs):

        data = kwargs
        if identifier is not None:
            data["id"] = identifier
        return self.requester.get(self.route, **data)

    def delete(
        self,
        identifier: str,
        data: Optional[Union[List, Dict]] = None,
        return_response: bool = False,
        **kwargs,
    ):
        data = data or {}
        if identifier and not isinstance(data, list):
            data["id"] = identifier
        return self.requester.delete(
            self.route, data=data, return_response=return_response, **kwargs
        )

    def post(
        self,
        data: Optional[Union[List, Dict]] = None,
        return_response: bool = False,
        clear_unused: bool = True,
        **kwargs,
    ):
        data = data if data is not None else {}
        if isinstance(data, list):
            data = (
                [self._clear_unused(x) for x in data] if clear_unused is True else data
            )
        else:
            data = self._clear_unused(data) if clear_unused is True else data
        return self.requester.post(
            self.route, return_response=return_response, data=data, **kwargs
        )

    def put(
        self,
        identifier: str,
        data: Union[List, Dict],
        return_response: bool = False,
        clear_unused: bool = True,
        **kwargs,
    ):
        if identifier and not isinstance(data, list):
            data["id"] = identifier
        data = self._clear_unused(data) if clear_unused is True else data
        return self.requester.put(
            self.route, return_response=return_response, data=data, **kwargs
        )
