from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from resources.db_creds import DbCreds


_db_creds = DbCreds.get_creds()
_database = _db_creds.pop("dbname")
_db_creds["username"] = _db_creds.pop("user")
_engine = create_engine(
    URL.create("postgresql+psycopg2", database=_database, **_db_creds),
    pool_pre_ping=True,
)
_SessionFactory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)


def get_db_session() -> Session:
    """Create a SQLAlchemy session for the configured PostgreSQL database."""
    return _SessionFactory()
