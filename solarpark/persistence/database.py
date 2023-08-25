from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from solarpark.settings import settings

engine = create_engine(f"{settings.CONNECTIONSTRING_DB}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_error_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):  # pylint: disable=W0613
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
