"""Declares :class:`Repository`."""
import logging
from typing import Any

from unimatrix.exceptions import CanonicalException

from .aggregateroot import AggregateRoot
from .const import DEFAULT_LOGGER_NAME
from .factory import Factory


class Repository:
    """Provide a base class implementation for DDD repositories."""
    __module__: str = 'ddd'
    logger: logging.Logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    @property
    def factory(self) -> Factory:
        """The :class:`ddd.Factory` implementation that is used to reconstruct
        :class:`ddd.AggregateRoot` instance from the persistence backend.
        """
        raise NotImplementedError

    async def exists(self, *args, **kwargs) -> bool:
        """Return a boolean indicating if the :class:`ddd.AggregateRoot`
        specified by the input parameters exists.
        """
        raise NotImplementedError

    async def persist(self, obj: Any) -> Any:
        """Persist an :class:`~ddd.AggregateRoot` instance and return the
        instance, reflecting any data changes that were made during the
        persist.
        """
        raise NotImplementedError

    async def __aenter__(self):
        if hasattr(self, 'setup_context'):
            await self.setup_context()
        return self

    async def __aexit__(self, type, exception, traceback) -> bool:
        suppress = False
        if hasattr(self, 'teardown_context'):
            suppress = await self.teardown_context(type, exception, traceback)
        return bool(suppress)


    class DoesNotExist(CanonicalException):
        code = 'RESOURCE_DOES_NOT_EXIST'
        http_status_code = 404
        message = (
            "The entity specified by the request parameters does not exist."
        )
