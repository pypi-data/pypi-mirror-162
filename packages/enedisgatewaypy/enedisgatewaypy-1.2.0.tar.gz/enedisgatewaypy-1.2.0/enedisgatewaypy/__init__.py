# -*- coding:utf-8 -*-

"""Provides authentification and row access to Enedis Gateway website."""
from .enedisgateway import EnedisGateway, EnedisByPDL
from .exceptions import EnedisException, LimitReached, GatewayException

name = "EnedisGateway"
__version__ = "1.2.0"
__all__ = ["EnedisGateway", "EnedisByPDL", "EnedisException", "LimitReached", "GatewayException"]
