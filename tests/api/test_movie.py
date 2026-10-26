import pytest
from data.movie import MovieData


@pytest.mark.api
@pytest.mark.smoke
def test_create_movie(authenticated_api_manager):
    movie_data = MovieData.create_movie_payload()
    response = authenticated_api_manager.movies_api.create_movie(movie_data)
    response_data = response.json()

    assert "id" in response_data
    assert response_data["name"] == movie_data["name"]
    assert response_data["price"] == movie_data["price"]

    authenticated_api_manager.movies_api.delete_movie(response_data["id"])


@pytest.mark.api
@pytest.mark.smoke
def test_get_movie_by_id(authenticated_api_manager, created_movie):
    movie_id = created_movie["id"]
    movie_name = created_movie["data"]["name"]

    response = authenticated_api_manager.movies_api.get_movie_by_id(movie_id)
    response_data = response.json()

    assert response_data["id"] == movie_id
    assert response_data["name"] == movie_name


@pytest.mark.api
def test_get_movies_with_filter(authenticated_api_manager):
    params = {"genreId": 9, "pageSize": 5}
    response = authenticated_api_manager.movies_api.get_movies(params=params)
    response_data = response.json()

    assert "movies" in response_data
    assert len(response_data["movies"]) <= 5

    assert all(m["genreId"] == 9 for m in response_data["movies"])


@pytest.mark.api
@pytest.mark.regression
def test_update_movie(authenticated_api_manager, created_movie):
    movie_id = created_movie["id"]
    new_movie_data = MovieData.create_movie_payload()

    response = authenticated_api_manager.movies_api.update_movie(movie_id, new_movie_data)
    response_data = response.json()

    assert response_data["name"] == new_movie_data["name"]
    assert response_data["price"] == new_movie_data["price"]

    get_response = authenticated_api_manager.movies_api.get_movie_by_id(movie_id)
    get_response_data = get_response.json()

    assert get_response_data["name"] == new_movie_data["name"]
    assert get_response_data["price"] == new_movie_data["price"]


@pytest.mark.api
@pytest.mark.regression
def test_delete_movie(authenticated_api_manager):
    movie_data = MovieData.create_movie_payload()
    create_response = authenticated_api_manager.movies_api.create_movie(movie_data)
    movie_id = create_response.json()["id"]
    authenticated_api_manager.movies_api.delete_movie(movie_id)
    authenticated_api_manager.movies_api.get_movie_by_id(movie_id, expected_status=404)


@pytest.mark.api
@pytest.mark.regression
def test_create_movie_without_name(authenticated_api_manager):
    movie_data = MovieData.create_movie_payload()
    del movie_data["name"]

    authenticated_api_manager.movies_api.create_movie(movie_data, expected_status=400)


@pytest.mark.api
@pytest.mark.regression
def test_get_nonexistent_movie(authenticated_api_manager):
    authenticated_api_manager.movies_api.get_movie_by_id(9999999, expected_status=404)


@pytest.mark.api
@pytest.mark.regression
def test_update_nonexistent_movie(authenticated_api_manager):
    new_movie_data = MovieData.create_movie_payload()
    authenticated_api_manager.movies_api.update_movie(
        9999999,
        new_movie_data,
        expected_status=404
    )


@pytest.mark.api
@pytest.mark.regression
def test_delete_nonexistent_movie(authenticated_api_manager):
    authenticated_api_manager.movies_api.delete_movie(
        9999999,
        expected_status=404
    )
