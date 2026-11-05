from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATABASE_URL
from app.models.basemodel import Base

engine_options = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_options)

if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def register_unicode_casefold(dbapi_connection, _connection_record):
        dbapi_connection.create_function(
            "casefold",
            1,
            lambda value: value.casefold() if value is not None else None,
            deterministic=True,
        )

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
