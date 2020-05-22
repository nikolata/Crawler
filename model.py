from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
import datetime


class Websites(Base):
    __tablename__ = 'websites'
    url_id = Column(Integer, primary_key=True)
    website_link = Column(String)
    server = Column(String)
    parent_id = Column(Integer)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    used = Column(Boolean, default=False)


class Counter(Base):
    __tablename__ = 'counter'
    counter_id = Column(Integer, primary_key=True)
    curr_id = Column(Integer)
