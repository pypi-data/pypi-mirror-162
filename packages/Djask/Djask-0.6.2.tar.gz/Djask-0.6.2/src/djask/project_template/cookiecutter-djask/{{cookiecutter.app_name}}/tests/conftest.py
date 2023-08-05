import pytest
from {{cookiecutter.app_name}} import create_app


@pytest.fixture
def app():
    _app = create_app("testing")
    _ctx = app.test_request_context()
    _ctx.push()

    # refresh the database
    _app.db.drop_all()
    _app.db.create_all()

    yield _app

    _app.db.session.remove()
    _app.db.drop_all()
    _ctx.pop()


@pytest.fixture
def client(app):
    yield app.test_client()
