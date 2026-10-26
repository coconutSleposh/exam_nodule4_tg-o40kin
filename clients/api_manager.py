from clients.movie_api import MoviesApi
from clients.auth_api import AuthApi

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session)
        self.movies_api = MoviesApi(session)