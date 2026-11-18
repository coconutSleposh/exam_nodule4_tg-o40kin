from sqlalchemy.orm import Session

from db_models.movies import MovieDBModel


class DBHelper:
    """Database queries used by the Movies API exam tests."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_movie_by_id(self, movie_id: int) -> MovieDBModel | None:
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.id == movie_id).first()

    def get_movie_by_name(self, name: str) -> MovieDBModel | None:
        return self.db_session.query(MovieDBModel).filter(MovieDBModel.name == name).first()
