import os
import sys

sys.path.append(os.getcwd)

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///one_to_many.db')

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'

    game_id = Column(Integer(), primary_key=True)
    game_title = Column(String())
    game_genre = Column(String())
    game_platform = Column(String())
    game_price = Column(Integer())

    reviews = relationship('Review', backref=backref('game'))

    def __repr__(self):
        return f'Game(id={self.game_id}, ' + \
            f'title={self.game_title}, ' + \
            f'platform={self.game_platform})'

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer(), primary_key=True)
    review_score = Column(Integer())
    review_comment = Column(String())
    game_id = Column(Integer(), ForeignKey('games.game_id'))

    def __repr__(self):
        return f'Review(id={self.review_id}, ' + \
            f'score={self.review_score}, ' + \
            f'game_id={self.game_id})'
