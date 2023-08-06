"""Declares :class:`AggregateRoot`."""
import typing
import logging

from .const import DEFAULT_LOGGER_NAME


class AggregateRoot:
    """Encapsulates a domain model and represents an atomic unit through which
    data changes are made.
    """
    __module__: str = 'ddd'
    logger: logging.Logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    def get_identifier(self) -> typing.Any:
        """Return the identifier for the domain object."""
        raise NotImplementedError
