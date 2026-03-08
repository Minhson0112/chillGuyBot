from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from bot.config.config import DB_CONFIG

Base = declarative_base()

dbUrl = (
    f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

engine = create_engine(dbUrl, echo=False)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def getDbSession():
    session = sessionLocal()
    try:
        yield session
    finally:
        session.close()