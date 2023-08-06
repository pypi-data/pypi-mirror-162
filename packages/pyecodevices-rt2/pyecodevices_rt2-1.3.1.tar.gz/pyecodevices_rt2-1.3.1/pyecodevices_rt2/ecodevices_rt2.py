from datetime import datetime
from datetime import timedelta

import requests

from .const import INDEX_GET_LINK
from .const import PRODUCT_ENTRY
from .const import PRODUCT_VALUE
from .const import RESPONSE_ENTRY
from .const import RESPONSE_SUCCESS_VALUE
from .const import RT2_API_GET_LINK_CACHED
from .exceptions import EcoDevicesRT2ConnectError
from .exceptions import EcoDevicesRT2RequestError


class EcoDevicesRT2:
    """Class representing the Ecodevices RT2 and its API"""

    def __init__(
        self,
        host: str,
        port: int = 80,
        apikey: str = "",
        timeout: int = 10,
        cached_ms: int = 0,
    ):
        self._host = host
        self._port = port
        self._apikey = apikey
        self._apiurl = "http://%s:%s/api/xdevices.json?key=%s" % (
            str(host),
            str(port),
            str(apikey),
        )
        self._timeout = timeout
        self._cached_ms = cached_ms
        self._cached = RT2_API_GET_LINK_CACHED

    @property
    def host(self):
        """Return the hostname."""
        return self._host

    @property
    def apikey(self):
        """Return the apikey."""
        return self._apikey

    @property
    def apiurl(self):
        """Return the default apiurl."""
        return self._apiurl

    @property
    def cached_ms(self):
        """Return the maximum cached value in milliseconds."""
        return self._cached_ms

    def _request(self, params):
        r = requests.get(self._apiurl, params=params, timeout=self._timeout)
        r.raise_for_status()
        content = r.json()
        product = content.get(PRODUCT_ENTRY, None)
        if product == PRODUCT_VALUE:
            return content
        else:
            raise EcoDevicesRT2ConnectError(
                "Ecodevices RT2 API wrong 'product' name\nUrl: %s \nValues: %s"
                % (r.request.url, content)
            )

    def ping(self) -> bool:
        try:
            return (
                self.get(INDEX_GET_LINK, command_entry=RESPONSE_ENTRY)
                == RESPONSE_SUCCESS_VALUE
            )
        except:
            pass
        return False

    def get_all_cached(self):
        for complete_command in self._cached:
            self.get(complete_command, cached_ms=0)
        return self._cached

    def get(
        self, command, command_value=None, command_entry=None, cached_ms: int = None
    ):
        """Get value from api : http://{host}:{port}/api/xdevices.json?key={apikey}&{command}={command_value},
        then get value {command_entry} in JSON response."""
        complete_command = command
        if command_value is not None:
            complete_command = command + "=" + command_value
        if cached_ms is None:
            cached_ms = self._cached_ms

        response = None
        now = datetime.now()
        if (
            complete_command in self._cached
            and "last_call" in self._cached[complete_command]
        ):
            last_call = self._cached[complete_command]["last_call"]
            if (now - last_call) / timedelta(
                milliseconds=1
            ) <= cached_ms and "response" in self._cached[complete_command]:
                response = self._cached[complete_command]["response"]

        if response is None and cached_ms < 0:
            response = {}

        if response is None:
            response = self._request(complete_command)
            if complete_command in self._cached:
                self._cached[complete_command]["last_call"] = now
                self._cached[complete_command]["response"] = response

        if command_entry is not None:
            if command_entry in response:
                response = response.get(command_entry)
            else:
                raise EcoDevicesRT2RequestError(
                    "Ecodevices RT2 API error, key '%s' not in return from command: %s \nValues: %s"
                    % (command_entry, complete_command, response)
                )
        return response
