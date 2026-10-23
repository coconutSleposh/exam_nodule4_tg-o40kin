import pytest
import requests
from clients.movie_api import MoviesApi
from clients.auth_api import AuthApi
from data.movie import MovieData

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def movies_api(session):
    return MoviesApi(session)

@pytest.fixture(scope="session")
def authenticated_movies_api(movies_api):
    auth_api = AuthApi(movies_api.session)
    response = auth_api.login("api1@gmail.com", "asdqwe123Q")
    token = response.json()["accessToken"]
    movies_api._update_session_headers({"Authorization": "Bearer " + token})
    return movies_api

@pytest.fixture
def created_movie(authenticated_movies_api):
    movie_data = MovieData.create_movie_payload()
    response = authenticated_movies_api.create_movie(movie_data)
    movie_id = response.json()["id"]
    yield {"id": movie_id, "data": movie_data}
    try:
        authenticated_movies_api.delete_movie(movie_id)
    except ValueError:
        pass