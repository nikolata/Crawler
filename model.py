from database import Base
from sqlalchemy import Column, Integer, String


class Websites(Base):
    __tablename__ = 'websites'
    url_id = Column(Integer, primary_key=True)
    website_link = Column(String, unique=True)
    server = Column(String)
    parent_id = Column(Integer)


class Counter(Base):
    __tablename__ = 'counter'
    counter_id = Column(Integer, primary_key=True)
    curr_id = Column(Integer)
