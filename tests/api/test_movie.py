import pytest
from data.movie import MovieData


@pytest.mark.api
@pytest.mark.smoke
def test_create_movie(super_admin):
    movie_data = MovieData.create_movie_payload()
    response = super_admin.api.movies_api.create_movie(movie_data)
    response_data = response.json()

    assert "id" in response_data
    assert response_data["name"] == movie_data["name"]
    assert response_data["price"] == movie_data["price"]

    super_admin.api.movies_api.delete_movie(response_data["id"])


@pytest.mark.api
@pytest.mark.smoke
def test_get_movie_by_id(super_admin, created_movie):
    movie_id = created_movie["id"]
    movie_name = created_movie["data"]["name"]

    response = super_admin.api.movies_api.get_movie_by_id(movie_id)
    response_data = response.json()

    assert response_data["id"] == movie_id
    assert response_data["name"] == movie_name


@pytest.mark.api
def test_get_movies_with_filter(super_admin):
    params = {"genreId": 9, "pageSize": 5}
    response = super_admin.api.movies_api.get_movies(params=params)
    response_data = response.json()

    assert "movies" in response_data
    assert len(response_data["movies"]) <= 5

    assert all(m["genreId"] == 9 for m in response_data["movies"])


@pytest.mark.api
@pytest.mark.regression
def test_update_movie(super_admin, created_movie):
    movie_id = created_movie["id"]
    new_movie_data = MovieData.create_movie_payload()

    response = super_admin.api.movies_api.update_movie(movie_id, new_movie_data)
    response_data = response.json()

    assert response_data["name"] == new_movie_data["name"]
    assert response_data["price"] == new_movie_data["price"]

    get_response = super_admin.api.movies_api.get_movie_by_id(movie_id)
    get_response_data = get_response.json()

    assert get_response_data["name"] == new_movie_data["name"]
    assert get_response_data["price"] == new_movie_data["price"]


@pytest.mark.api
@pytest.mark.regression
def test_delete_movie(super_admin):
    movie_data = MovieData.create_movie_payload()
    create_response = super_admin.api.movies_api.create_movie(movie_data)
    movie_id = create_response.json()["id"]
    super_admin.api.movies_api.delete_movie(movie_id)
    super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)


@pytest.mark.api
@pytest.mark.regression
def test_create_movie_without_name(super_admin):
    movie_data = MovieData.create_movie_payload()
    del movie_data["name"]

    super_admin.api.movies_api.create_movie(movie_data, expected_status=400)


@pytest.mark.api
@pytest.mark.regression
def test_get_nonexistent_movie(super_admin):
    super_admin.api.movies_api.get_movie_by_id(9999999, expected_status=404)


@pytest.mark.api
@pytest.mark.regression
def test_update_nonexistent_movie(super_admin):
    new_movie_data = MovieData.create_movie_payload()
    super_admin.api.movies_api.update_movie(
        9999999,
        new_movie_data,
        expected_status=404
    )


@pytest.mark.api
@pytest.mark.regression
def test_delete_nonexistent_movie(super_admin):
    super_admin.api.movies_api.delete_movie(
        9999999,
        expected_status=404
    )


def test_create_movie_by_common_user(common_user):
    movie_data = MovieData.create_movie_payload()

    common_user.api.movies_api.create_movie(
        movie_data,
        expected_status=403
    )


@pytest.mark.parametrize('filter_params, check_type',
                         [
                             ({"minPrice": 100}, "price"),
                             ({"locations": "MSK"}, "location")
                         ])
def test_get_movie(super_admin, filter_params, check_type):
    response = super_admin.api.movies_api.get_movies(params=filter_params)
    movies = response.json()["movies"]

    assert len(movies) > 0, "Сервер вернул пустой список фильмов"

    if check_type == "price":
        for movie in movies:
            assert movie["price"] >= 100, f"Фильм {movie['name']} стоит меньше 100"

    elif check_type == "location":
        for movie in movies:
            assert movie["location"] == "MSK", f"Фильм {movie['name']} не из Москвы"


@pytest.mark.parametrize('role,expected_status',
                         [
                             ('super_admin',200),
                             ('common_user',403)
                         ])
def test_delete_movie(super_admin, common_user, created_movie, role, expected_status):
    if role == 'super_admin':
        user = super_admin
    elif role == 'common_user':
        user = common_user

    movie_id = created_movie["id"]

    user.api.movies_api.delete_movie(
        movie_id,
        expected_status=expected_status
    )


@pytest.mark.api
@pytest.mark.database
def test_create_and_delete_movie_are_reflected_in_db(super_admin, db_helper):
    movie_data = MovieData.create_movie_payload()
    movie_name = movie_data["name"]
    movie_id = None

    assert db_helper.get_movie_by_name(movie_name) is None

    try:
        create_response = super_admin.api.movies_api.create_movie(movie_data)
        movie_id = create_response.json()["id"]

        movie_in_db = db_helper.get_movie_by_id(movie_id)
        assert movie_in_db is not None
        assert movie_in_db.name == movie_name

        deleted_movie_id = movie_id
        super_admin.api.movies_api.delete_movie(deleted_movie_id)
        movie_id = None

        assert db_helper.get_movie_by_id(deleted_movie_id) is None
        assert db_helper.get_movie_by_name(movie_name) is None
    finally:
        if movie_id is not None:
            try:
                super_admin.api.movies_api.delete_movie(movie_id)
            except ValueError:
                pass
