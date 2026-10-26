from custom_requester.custom_requester import CustomRequester
from config.base_urls import MOVIES_BASE_URL


class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_BASE_URL)

    def create_movie(self, movie_data, **kwargs):
        expected = kwargs.pop("expected_status", 201)
        return self.send_request(
            method="POST",
            endpoint="/movies",
            data=movie_data,
            expected_status=expected,
            **kwargs
        )

    def get_movies(self, **kwargs):
        expected = kwargs.pop("expected_status", 200)
        params = kwargs.pop("params", None)
        return self.send_request(
            method="GET",
            endpoint="/movies",
            params=params,
            expected_status=expected,
            **kwargs
        )

    def get_movie_by_id(self, movie_id, **kwargs):
        expected = kwargs.pop("expected_status", 200)
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected,
            **kwargs
        )

    def delete_movie(self, movie_id, **kwargs):
        expected = kwargs.pop("expected_status", 200)
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected,
            **kwargs
        )

    def update_movie(self, movie_id, movie_data, **kwargs):
        expected = kwargs.pop("expected_status", 200)
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}",
            data=movie_data,
            expected_status=expected,
            **kwargs
        )
