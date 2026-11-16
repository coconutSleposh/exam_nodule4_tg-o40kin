import pytest

from db_models.movies import MovieDBModel


@pytest.mark.database
def test_created_test_user_is_available_through_db_helper(db_helper, created_test_user):
    user_from_db = db_helper.get_user_by_id(created_test_user.id)

    assert user_from_db is not None
    assert user_from_db.email == created_test_user.email
    assert db_helper.get_user_by_email(created_test_user.email).id == created_test_user.id
    assert db_helper.user_exists_by_email(created_test_user.email)


@pytest.mark.database
def test_movie_model_reads_existing_movie(db_session, db_helper):
    movie = db_session.query(MovieDBModel).first()

    assert movie is not None, "The movies table contains no rows to verify the mapping"
    assert db_helper.get_movie_by_id(movie.id).name == movie.name
    assert db_helper.get_movie_by_name(movie.name).id == movie.id
