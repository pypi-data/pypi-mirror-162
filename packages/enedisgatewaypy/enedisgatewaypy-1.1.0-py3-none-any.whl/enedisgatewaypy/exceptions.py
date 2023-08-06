import logging

_LOGGER = logging.getLogger(__name__)


class EnedisException(Exception):
    """Enedis exception."""


class EnedisLimitReached(Exception):
    """Limit reached exception."""


class EnedisGatewayException(EnedisException):
    """Enedis gateway error."""

    def __init__(self, message):
        """Initialize."""
        super().__init__(message)
        _LOGGER.error(message)
