# -*- coding: utf-8 -*-
import logging

from matos_aws_provider.lib.auth import Connection
from matos_aws_provider.lib.log import get_logger
from typing import Any

logger = get_logger()


class BaseProvider(Connection):
    def __init__(self, **kwargs) -> None:
        try:

            super().__init__(**kwargs)
            self._client_type = kwargs.pop("client_type")
            if self._client_type:
                self._conn = self.client(service_name=self._client_type)
        except Exception as ex:
            logging.error(ex)

    @property
    def conn(self) -> Any:
        if not self._conn:
            return None
        return self._conn

    @property
    def client_type(self) -> str:
        return self._client_type

    def get_inventory(self) -> Any:
        raise NotImplementedError

    def get_resources(self) -> Any:
        raise NotImplementedError
