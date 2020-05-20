from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


engine = create_engine("sqlite:///urls.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# @contextmanager
# def session_scope():
#     """Provide a transactional scope around a series of operations."""
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except (KeyboardInterrupt, SystemExit):
#         session.commit()
#         # except Exception as exc:
#         #     print(exc)
#         #     session.rollback()
#         #     raise
#     finally:
#         session.close()
