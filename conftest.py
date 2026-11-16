import pytest
import requests
from sqlalchemy.orm import Session
from clients.api_manager import ApiManager
from data.movie import MovieData
from resources.user_creds import SuperAdminCreds
from entities.user import User
from utils.data_generator import DataGenerator
from constants.roles import Roles
from models.base_models import TestUser
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

    api_manager.movies_api._update_session_headers({"Authorization": "Bearer " + token})
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


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user: TestUser) -> TestUser:
    return test_user.model_copy(update={"verified": True, "banned": False})


@pytest.fixture
def test_user() -> TestUser:
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.ADMIN.value],
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user


@pytest.fixture(scope="module")
def db_session() -> Session:
    """Provide a database session for a test module and close it afterward."""
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def db_helper(db_session: Session) -> DBHelper:
    return DBHelper(db_session)


@pytest.fixture(scope="function")
def created_test_user(db_helper: DBHelper):
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    try:
        yield user
    finally:
        existing_user = db_helper.get_user_by_id(user.id)
        if existing_user is not None:
            db_helper.delete_user(existing_user)
