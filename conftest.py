import pytest
import requests
from sqlalchemy.orm import Session

from clients.api_manager import ApiManager
from data.movie import MovieData
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper


@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="session")
def authenticated_api_manager(api_manager):
    response = api_manager.auth_api.login("api1@gmail.com", "asdqwe123Q")
    token = response.json()["accessToken"]
    api_manager.movies_api._update_session_headers({"Authorization": f"Bearer {token}"})
    return api_manager


@pytest.fixture
def created_movie(authenticated_api_manager):
    movie_data = MovieData.create_movie_payload()
    response = authenticated_api_manager.movies_api.create_movie(movie_data)
    movie_id = response.json()["id"]
    yield {"id": movie_id, "data": movie_data}
    try:
        authenticated_api_manager.movies_api.delete_movie(movie_id)
    except ValueError:
        pass


@pytest.fixture(scope="module")
def db_session() -> Session:
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def db_helper(db_session: Session) -> DBHelper:
    return DBHelper(db_session)
