import pytest
from sqlalchemy import select
from typing import Any, Type
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def assert_db_has(session: AsyncSession):
    async def _assert_db_has(model: Type[Any], where: dict):
        query = select(model).filter_by(**where)
        result = await session.execute(query)
        instance = result.scalars().first()
        assert instance is not None, (
            f"Expected {model.__name__} with {where} to exist, but it doesn't."
        )

    return _assert_db_has


@pytest.fixture
def assert_db_missing(session: AsyncSession):
    async def _assert_db_missing(model: Type[Any], where: dict):
        query = select(model).filter_by(**where)
        result = await session.execute(query)
        instance = result.scalars().first()
        assert instance is None, (
            f"Expected {model.__name__} with {where} to be missing, but it exists."
        )

    return _assert_db_missing


@pytest.fixture
def assert_db_count(session: AsyncSession):
    async def _assert_db_count(model: Type[Any], expected_count: int, where: dict | None = None):
        query = select(model)
        if where:
            query = query.filter_by(**where)
        result = await session.execute(query)
        count = len(result.scalars().all())

        assert count == expected_count, (
            f"Expected {expected_count} {model.__name__} records matching {where}, got {count}."
        )

    return _assert_db_count
