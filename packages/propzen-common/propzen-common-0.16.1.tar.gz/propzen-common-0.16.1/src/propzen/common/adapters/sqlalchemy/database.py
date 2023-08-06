from typing import Callable
from sqlalchemy import create_engine, orm, MetaData
from sqlalchemy.orm import Session


class Database:
    """Database session manager"""

    def __init__(self, db_url: str, sa_future: bool = False, sa_echo: bool = False,
                 sa_session_autocommit=False, sa_session_autoflush=False) -> None:
        self._database_created = False
        self._engine = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=sa_echo,
            future=sa_future)
        self._session_factory = orm.sessionmaker(
            autocommit=sa_session_autocommit,
            autoflush=sa_session_autoflush,
            bind=self._engine)

    def create_database(self, metadata: MetaData, start_mappers: Callable) -> None:
        if not self._database_created:
            metadata.create_all(self._engine, checkfirst=True)
            start_mappers()
            self._database_created = True

    def session(self) -> Session:
        return self._session_factory()
