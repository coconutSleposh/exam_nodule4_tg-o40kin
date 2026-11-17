from uuid import uuid4

import allure
import pytest

from data.movie import MovieData
from db_models.movies import MovieDBModel
from models.base_models import MoviesPageResponse


pytestmark = pytest.mark.api


@pytest.mark.smoke
@allure.title("Создание фильма администратором")
@allure.description("Проверяет создание фильма и совпадение основных полей ответа с отправленными данными.")
def test_create_movie(super_admin):
    with allure.step("Подготавливаем данные фильма"):
        movie_data = MovieData.create_movie_payload()

    with allure.step("Создаём фильм через API"):
        response = super_admin.api.movies_api.create_movie(movie_data)
        response_data = response.json()

    with allure.step("Проверяем основные поля созданного фильма"):
        assert response_data["id"]
        assert response_data["name"] == movie_data["name"]
        assert response_data["price"] == movie_data["price"]

    with allure.step("Удаляем созданный фильм"):
        super_admin.api.movies_api.delete_movie(response_data["id"])


@pytest.mark.smoke
@allure.title("Получение фильма по идентификатору")
@allure.description("Проверяет, что GET /movies/{id} возвращает созданный фильм с ожидаемыми данными.")
def test_get_movie_by_id(super_admin, created_movie):
    movie_id = created_movie["id"]
    movie_name = created_movie["data"]["name"]

    with allure.step(f"Запрашиваем фильм с id={movie_id}"):
        response = super_admin.api.movies_api.get_movie_by_id(movie_id)
        response_data = response.json()

    with allure.step("Проверяем id и название фильма"):
        assert response_data["id"] == movie_id
        assert response_data["name"] == movie_name


@pytest.mark.smoke
@allure.title("Список фильмов соответствует схеме и фильтру")
@allure.description("Проверяет структуру страницы /movies, размер выдачи и genreId каждого фильма.")
def test_get_movies_with_filter(super_admin):
    params = {"genreId": 9, "pageSize": 5}
    with allure.step("Получаем страницу фильмов с фильтрами"):
        response = super_admin.api.movies_api.get_movies(params=params)
        response_data = MoviesPageResponse.model_validate(response.json())

    with allure.step("Проверяем размер страницы и жанр результатов"):
        assert len(response_data.movies) <= params["pageSize"]
        assert all(movie.genreId == params["genreId"] for movie in response_data.movies)


@pytest.mark.regression
@allure.title("Обновление фильма")
@allure.description("Проверяет, что PATCH сохраняет новые данные и они видны при повторном GET.")
def test_update_movie(super_admin, created_movie):
    movie_id = created_movie["id"]
    new_movie_data = MovieData.create_movie_payload()

    with allure.step("Обновляем фильм"):
        response = super_admin.api.movies_api.update_movie(movie_id, new_movie_data)
        response_data = response.json()

    with allure.step("Проверяем ответ на обновление"):
        assert response_data["name"] == new_movie_data["name"]
        assert response_data["price"] == new_movie_data["price"]

    with allure.step("Повторно запрашиваем фильм и проверяем сохранение изменений"):
        get_response = super_admin.api.movies_api.get_movie_by_id(movie_id)
        get_response_data = get_response.json()

        assert get_response_data["name"] == new_movie_data["name"]
        assert get_response_data["price"] == new_movie_data["price"]


@pytest.mark.database
@pytest.mark.regression
@allure.title("Удаление фильма удаляет запись из БД")
@allure.description("Создаёт временную запись фильма, удаляет её через API и проверяет отсутствие записи в БД.")
def test_delete_movie(super_admin, db_session, db_helper):
    """Seed a known movie row when absent, then verify API deletion in DB."""
    movie_id = 54
    movie_data = {
        "name": f"delete-test-{uuid4().hex}",
        "price": 100,
        "description": "Temporary movie for the deletion test",
        "image_url": None,
        "location": "MSK",
        "published": False,
        "rating": 0.0,
        "genre_id": 5,
    }

    # Never delete an existing user's movie: use 54 only when it is free.
    if db_helper.get_movie_by_id(movie_id) is not None:
        movie_id = None
    movie = MovieDBModel(id=movie_id, **movie_data)
    db_session.add(movie)
    inserted = False
    try:
        db_session.commit()
        inserted = True
        movie_id = movie.id
        assert db_helper.get_movie_by_id(movie_id) is not None

        with allure.step(f"Удаляем фильм с id={movie_id} через API"):
            delete_response = super_admin.api.movies_api.delete_movie(movie_id)
            assert delete_response.status_code == 200
            get_response = super_admin.api.movies_api.get_movie_by_id(
                movie_id, expected_status=404
            )
            assert get_response.status_code == 404

        with allure.step("Проверяем, что запись удалена из базы данных"):
            db_session.expire_all()
            assert db_helper.get_movie_by_id(movie_id) is None
    finally:
        db_session.rollback()
        if inserted:
            db_session.expire_all()
            leftover = db_helper.get_movie_by_id(movie_id)
            if leftover is not None:
                db_session.delete(leftover)
                db_session.commit()


@pytest.mark.regression
@allure.title("Создание фильма без обязательного названия отклоняется")
@allure.description("Проверяет, что API отвечает статусом 400, если в запросе отсутствует name.")
def test_create_movie_without_name(super_admin):
    movie_data = MovieData.create_movie_payload()
    del movie_data["name"]

    with allure.step("Отправляем запрос без поля name и ожидаем 400"):
        super_admin.api.movies_api.create_movie(movie_data, expected_status=400)


@pytest.mark.regression
@allure.title("Получение несуществующего фильма возвращает 404")
def test_get_nonexistent_movie(super_admin):
    super_admin.api.movies_api.get_movie_by_id(9999999, expected_status=404)


@pytest.mark.regression
@allure.title("Обновление несуществующего фильма возвращает 404")
def test_update_nonexistent_movie(super_admin):
    new_movie_data = MovieData.create_movie_payload()
    super_admin.api.movies_api.update_movie(
        9999999,
        new_movie_data,
        expected_status=404
    )


@pytest.mark.regression
@allure.title("Удаление несуществующего фильма возвращает 404")
def test_delete_nonexistent_movie(super_admin):
    super_admin.api.movies_api.delete_movie(
        9999999,
        expected_status=404
    )


@pytest.mark.regression
@allure.title("Обычный пользователь не может создать фильм")
def test_create_movie_by_common_user(common_user):
    movie_data = MovieData.create_movie_payload()

    common_user.api.movies_api.create_movie(
        movie_data,
        expected_status=403
    )


@pytest.mark.smoke
@pytest.mark.parametrize('filter_params, check_type',
                         [
                             ({"minPrice": 100}, "price"),
                             ({"locations": "MSK"}, "location")
                         ])
@allure.title("Фильтрация списка фильмов по параметру {check_type}")
@allure.description("Проверяет, что каждый фильм в выдаче удовлетворяет переданному фильтру.")
def test_get_movie(super_admin, filter_params, check_type):
    with allure.step(f"Получаем список фильмов: {filter_params}"):
        response = super_admin.api.movies_api.get_movies(params=filter_params)
        movies_page = MoviesPageResponse.model_validate(response.json())
        movies = movies_page.movies

    assert len(movies) > 0, "Сервер вернул пустой список фильмов"

    if check_type == "price":
        for movie in movies:
            assert movie.price >= 100, f"Фильм {movie.name} стоит меньше 100"

    elif check_type == "location":
        for movie in movies:
            assert movie.location.value == "MSK", f"Фильм {movie.name} не из Москвы"


@pytest.mark.parametrize('role,expected_status',
                         [
                             ('super_admin',200),
                             ('common_user',403)
                         ])
@pytest.mark.regression
@allure.title("Права роли {role} на удаление фильма")
@allure.description("Администратор может удалить фильм, обычный пользователь получает отказ.")
def test_delete_movie_by_role(super_admin, common_user, created_movie, role, expected_status):
    if role == 'super_admin':
        user = super_admin
    elif role == 'common_user':
        user = common_user

    movie_id = created_movie["id"]

    user.api.movies_api.delete_movie(
        movie_id,
        expected_status=expected_status
    )


@pytest.mark.database
@allure.title("Создание и удаление фильма отражаются в БД")
@allure.description("Проверяет наличие созданного через API фильма в базе и его удаление.")
def test_create_and_delete_movie_are_reflected_in_db(super_admin, db_helper):
    movie_data = MovieData.create_movie_payload()
    movie_name = movie_data["name"]
    movie_id = None

    assert db_helper.get_movie_by_name(movie_name) is None

    try:
        with allure.step("Создаём фильм через API"):
            create_response = super_admin.api.movies_api.create_movie(movie_data)
            movie_id = create_response.json()["id"]

        with allure.step("Проверяем появление фильма в базе"):
            movie_in_db = db_helper.get_movie_by_id(movie_id)
            assert movie_in_db is not None
            assert movie_in_db.name == movie_name

        with allure.step("Удаляем фильм и проверяем, что записи больше нет"):
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
