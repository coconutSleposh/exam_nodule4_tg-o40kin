import allure
import pytest

from data.movie import MovieData
from models.base_models import FindOneMovieResponse, MovieResponse, MoviesPageResponse


@pytest.mark.api
@pytest.mark.smoke
@allure.title("Создание фильма администратором")
@allure.description("Проверяет создание фильма и совпадение основных полей ответа с отправленными данными.")
def test_create_movie(authenticated_api_manager):
    with allure.step("Подготавливаем данные фильма"):
        movie_data = MovieData.create_movie_payload()

    with allure.step("Создаём фильм через API"):
        response = authenticated_api_manager.movies_api.create_movie(movie_data)
        response_data = response.json()
        movie_id = response_data.get("id")

    try:
        with allure.step("Проверяем схему ответа созданного фильма"):
            created_movie = MovieResponse.model_validate(response_data)

        with allure.step("Сверяем данные фильма с запросом"):
            assert created_movie.name == movie_data["name"]
            assert created_movie.price == movie_data["price"]
    finally:
        if movie_id is not None:
            with allure.step("Удаляем созданный фильм"):
                try:
                    authenticated_api_manager.movies_api.delete_movie(movie_id)
                except ValueError:
                    pass


@pytest.mark.api
@pytest.mark.smoke
@allure.title("Получение фильма по идентификатору")
@allure.description("Проверяет, что GET /movies/{id} возвращает созданный фильм с ожидаемыми данными.")
def test_get_movie_by_id(authenticated_api_manager, created_movie):
    movie_id = created_movie["id"]
    movie_name = created_movie["data"]["name"]

    with allure.step(f"Запрашиваем фильм с id={movie_id}"):
        response = authenticated_api_manager.movies_api.get_movie_by_id(movie_id)
        movie = FindOneMovieResponse.model_validate(response.json())

    with allure.step("Проверяем схему, id и название фильма"):
        assert movie.id == movie_id
        assert movie.name == movie_name


@pytest.mark.api
@pytest.mark.smoke
@allure.title("Список фильмов соответствует схеме и фильтру")
@allure.description("Проверяет структуру страницы /movies, размер выдачи и genreId каждого фильма.")
def test_get_movies_with_filter(authenticated_api_manager):
    params = {"genreId": 9, "pageSize": 5}
    with allure.step("Получаем страницу фильмов с фильтрами"):
        response = authenticated_api_manager.movies_api.get_movies(params=params)
        response_data = MoviesPageResponse.model_validate(response.json())

    with allure.step("Проверяем размер страницы и жанр результатов"):
        assert len(response_data.movies) <= params["pageSize"]
        assert all(movie.genreId == params["genreId"] for movie in response_data.movies)


@pytest.mark.api
@pytest.mark.regression
@allure.title("Обновление фильма")
@allure.description("Проверяет, что PATCH сохраняет новые данные и они видны при повторном GET.")
def test_update_movie(authenticated_api_manager, created_movie):
    movie_id = created_movie["id"]
    new_movie_data = MovieData.create_movie_payload()

    with allure.step("Обновляем фильм"):
        response = authenticated_api_manager.movies_api.update_movie(movie_id, new_movie_data)
        updated_movie = MovieResponse.model_validate(response.json())

    with allure.step("Проверяем ответ на обновление"):
        assert updated_movie.name == new_movie_data["name"]
        assert updated_movie.price == new_movie_data["price"]

    with allure.step("Повторно запрашиваем фильм и проверяем сохранение изменений"):
        get_response = authenticated_api_manager.movies_api.get_movie_by_id(movie_id)
        fetched_movie = FindOneMovieResponse.model_validate(get_response.json())

        assert fetched_movie.name == new_movie_data["name"]
        assert fetched_movie.price == new_movie_data["price"]


@pytest.mark.api
@pytest.mark.regression
@allure.title("Создание фильма без обязательного названия отклоняется")
@allure.description("Проверяет, что API отвечает статусом 400, если в запросе отсутствует name.")
def test_create_movie_without_name(authenticated_api_manager):
    movie_data = MovieData.create_movie_payload()
    del movie_data["name"]

    with allure.step("Отправляем запрос без поля name и ожидаем 400"):
        authenticated_api_manager.movies_api.create_movie(movie_data, expected_status=400)


@pytest.mark.api
@pytest.mark.regression
@allure.title("Получение несуществующего фильма возвращает 404")
def test_get_nonexistent_movie(authenticated_api_manager):
    authenticated_api_manager.movies_api.get_movie_by_id(9999999, expected_status=404)


@pytest.mark.api
@pytest.mark.regression
@allure.title("Обновление несуществующего фильма возвращает 404")
def test_update_nonexistent_movie(authenticated_api_manager):
    new_movie_data = MovieData.create_movie_payload()
    authenticated_api_manager.movies_api.update_movie(
        9999999,
        new_movie_data,
        expected_status=404
    )


@pytest.mark.api
@pytest.mark.regression
@allure.title("Удаление несуществующего фильма возвращает 404")
def test_delete_nonexistent_movie(authenticated_api_manager):
    authenticated_api_manager.movies_api.delete_movie(
        9999999,
        expected_status=404
    )


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.parametrize('filter_params, check_type',
                         [
                             ({"minPrice": 100}, "price"),
                             ({"locations": "MSK"}, "location")
                         ])
@allure.title("Фильтрация списка фильмов по параметру {check_type}")
@allure.description("Проверяет, что каждый фильм в выдаче удовлетворяет переданному фильтру.")
def test_get_movie(authenticated_api_manager, filter_params, check_type):
    with allure.step(f"Получаем список фильмов: {filter_params}"):
        response = authenticated_api_manager.movies_api.get_movies(params=filter_params)
        movies_page = MoviesPageResponse.model_validate(response.json())
        movies = movies_page.movies

    assert len(movies) > 0, "Сервер вернул пустой список фильмов"

    if check_type == "price":
        for movie in movies:
            assert movie.price >= 100, f"Фильм {movie.name} стоит меньше 100"

    elif check_type == "location":
        for movie in movies:
            assert movie.location.value == "MSK", f"Фильм {movie.name} не из Москвы"


@pytest.mark.api
@pytest.mark.database
@allure.title("Создание и удаление фильма отражаются в бд")
@allure.description("Проверяет наличие созданного через api фильма в базе и его удаление.")
def test_create_and_delete_movie_are_reflected_in_db(authenticated_api_manager, db_helper):
    movie_data = MovieData.create_movie_payload()
    movie_name = movie_data["name"]
    movie_id = None

    assert db_helper.get_movie_by_name(movie_name) is None

    try:
        with allure.step("Создаём фильм через апи"):
            create_response = authenticated_api_manager.movies_api.create_movie(movie_data)
            response_data = create_response.json()
            movie_id = response_data.get("id")
            created_movie = MovieResponse.model_validate(response_data)
            movie_id = created_movie.id

        with allure.step("Проверяем появление фильма в базе"):
            movie_in_db = db_helper.get_movie_by_id(movie_id)
            assert movie_in_db is not None
            assert movie_in_db.name == movie_name

        with allure.step("Удаляем фильм и проверяем, что записи больше нет"):
            deleted_movie_id = movie_id
            authenticated_api_manager.movies_api.delete_movie(deleted_movie_id)
            movie_id = None

            assert db_helper.get_movie_by_id(deleted_movie_id) is None
            assert db_helper.get_movie_by_name(movie_name) is None
    finally:
        if movie_id is not None:
            try:
                authenticated_api_manager.movies_api.delete_movie(movie_id)
            except ValueError:
                pass
