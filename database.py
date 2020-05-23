from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import scoped_session


engine = create_engine("sqlite:///urls.db")
Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        print('this website is already added')
        session.rollback()
    finally:
        session.close()

Session.remove()