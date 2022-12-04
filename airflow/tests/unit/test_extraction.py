import pytest

from sqlalchemy import create_engine

@pytest.fixture(scope='session')
def connection():
    engine = create_engine(
        ""
    )