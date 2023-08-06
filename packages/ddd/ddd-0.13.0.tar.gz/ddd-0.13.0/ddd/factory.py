"""Declares :class:`Factory`."""
import logging

from .aggregateroot import AggregateRoot
from .const import DEFAULT_LOGGER_NAME


class Factory:
    """Provides an interface to (re)build domain objects."""
    __module__: str = 'ddd'
    logger: logging.Logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    @property
    def model(self) -> AggregateRoot:
        """The domain model (:class:`ddd.AggregateRoot`) that is created by the
        concrete :class:`Factory` implementation.
        """
        raise NotImplementedError

    def fromdao(self, dao: object) -> AggregateRoot:
        """Reconstruct a domain object (:class:`ddd.AggregateRoot`)
        from the data storage layer. The default implementation raises
        a :exc:`NotImplementedError`.
        """
        raise NotImplementedError
