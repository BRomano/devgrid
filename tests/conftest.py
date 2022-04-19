import pytest
from devgrid import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c
