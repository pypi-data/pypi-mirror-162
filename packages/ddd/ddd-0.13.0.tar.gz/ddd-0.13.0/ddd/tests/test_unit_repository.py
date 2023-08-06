# pylint: skip-file
import asyncio
import unittest.mock

import pytest

from ..repository import Repository


@pytest.mark.asyncio
class TestRepository:

    class repo_class(Repository):
        factory = None

    async def test_context_without_setup_functions(self):
        async with self.repo_class():
            pass

    async def test_context_setup_is_invoked(self):
        repo = self.repo_class()
        repo.setup_context = unittest.mock.AsyncMock()

        async with repo:
            pass
        repo.setup_context.assert_called_once_with()

    async def test_context_teardown_is_invoked(self):
        repo = self.repo_class()
        repo.teardown_context = unittest.mock.AsyncMock()

        async with repo:
            pass
        repo.teardown_context.assert_called_once_with(None, None, None)
