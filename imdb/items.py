# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImdbItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, String, JSON)
DeclarativeBase = declarative_base()


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Movies(DeclarativeBase):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250))
    url = Column(String(250))
    genre = Column(String(250))
    year = Column(String(100))
    path = Column(String(100))
    country = Column(String(100))
    gross = Column(String(100))
    budget = Column(String(100))
    director_data = Column(JSON)
    writer_data = Column(JSON)
    producer_data = Column(JSON)
    release_dates = Column(JSON)
    production_data = Column(JSON)
    distributors_data = Column(JSON)
    awards = Column(JSON)
