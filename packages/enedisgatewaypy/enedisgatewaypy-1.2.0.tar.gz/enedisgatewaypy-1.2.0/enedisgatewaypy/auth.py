"""Class for Enedis Authentification (http://enedisgateway.tech)."""
from __future__ import annotations

import logging

from aiohttp import ClientSession, ClientError, ClientResponse
from .exceptions import EnedisException, GatewayException, LimitReached

URL = "https://enedisgateway.tech"

_LOGGER = logging.getLogger(__name__)


class EnedisAuth:
    """Class for Enedis Auth API."""

    def __init__(self, token, session=None):
        """Init."""
        self.token = token
        self.session = session if session else ClientSession()

    async def async_close(self):
        """Close session."""
        await self.session.close()

    async def request(self, method: str = "POST", path: str = "api", **kwargs) -> ClientResponse:
        """Request session."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if kwargs.get("json"):
            headers["Content-Type"] = "application/json"

        headers["Authorization"] = self.token

        try:
            _LOGGER.debug("Request %s", kwargs)
            resp = await self.session.request(
                method, f"{URL}/{path}", **kwargs, headers=headers, timeout=5
            )

            response = await resp.json()
            _LOGGER.debug("Response %s", response)

            if "tag" in response and response["tag"] in [
                "limit_reached",
                "enedis_return_ko",
            ]:
                raise LimitReached(response.get("description"))

            if "error" in response:
                raise GatewayException(response.get("error"))

            return response
        except ClientError as error:
            raise EnedisException from error
