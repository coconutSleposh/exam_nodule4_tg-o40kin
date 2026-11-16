from custom_requester.custom_requester import CustomRequester
from config.base_urls import MOVIES_BASE_URL


class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)

    def create_movie(self, movie_data, expected_status=201, **kwargs):
        return self.send_request(
            method="POST",
            endpoint="/movies",
            data=movie_data,
            expected_status=expected_status,
            **kwargs
        )

    def get_movies(self, params=None, expected_status=200, **kwargs):
        return self.send_request(
            method="GET",
            endpoint="/movies",
            params=params,
            expected_status=expected_status,
            **kwargs
        )

    def get_movie_by_id(self, movie_id, expected_status=200, **kwargs):
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status,
            **kwargs
        )

    def delete_movie(self, movie_id, expected_status=200, **kwargs):
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status,
            **kwargs
        )

    def update_movie(self, movie_id, movie_data, expected_status=200, **kwargs):
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}",
            data=movie_data,
            expected_status=expected_status,
            **kwargs
        )


class UserApi(CustomRequester):
    USER_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.USER_BASE_URL)

    def get_user(self, user_locator, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"user/{user_locator}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint="user",
            data=user_data,
            expected_status=expected_status
        )
