import pytest
from data.movie import MovieData


def test_create_movie(authenticated_movies_api):
    movie_data = MovieData.create_movie_payload()
    response = authenticated_movies_api.create_movie(movie_data)
    response_data = response.json()

    assert "id" in response_data
    assert response_data["name"] == movie_data["name"]
    assert response_data["price"] == movie_data["price"]


def test_get_movie_by_id(authenticated_movies_api, created_movie):
    movie_id = created_movie["id"]
    movie_name = created_movie["data"]["name"]

    response = authenticated_movies_api.get_movie_by_id(movie_id)
    response_data = response.json()

    assert response_data["id"] == movie_id
    assert response_data["name"] == movie_name


def test_get_movies_with_filter(authenticated_movies_api):
    params = {"genreId": 9, "pageSize": 5}
    response = authenticated_movies_api.get_movies(params=params)
    response_data = response.json()

    assert "movies" in response_data
    assert len(response_data["movies"]) <= 5


def test_delete_movie(authenticated_movies_api, created_movie):
    movie_id = created_movie["id"]

    authenticated_movies_api.delete_movie(movie_id)

    authenticated_movies_api.get_movie_by_id(movie_id, expected_status=404)


def test_create_movie_without_name(authenticated_movies_api):
    movie_data = MovieData.create_movie_payload()
    del movie_data["name"]

    authenticated_movies_api.create_movie(movie_data, expected_status=400)


def test_get_nonexistent_movie(authenticated_movies_api):
    authenticated_movies_api.get_movie_by_id(9999999, expected_status=404)
