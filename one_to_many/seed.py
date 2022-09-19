#!/usr/bin/env python3

from faker import Faker
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Game, Review

if __name__ == '__main__':
    engine = create_engine('sqlite:///one_to_many.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Game).delete()
    session.query(Review).delete()

    fake = Faker()

    genres = ['action', 'adventure', 'strategy',
        'puzzle', 'first-person shooter', 'racing']
    platforms = ['nintendo 64', 'gamecube', 'wii', 'wii u', 'switch',
        'playstation', 'playstation 2', 'playstation 3', 'playstation 4',
        'playstation 5', 'xbox', 'xbox 360', 'xbox one', 'pc']

    games = []
    for i in range(50):
        game = Game(
            game_title=fake.unique.name(),
            game_genre=random.choice(genres),
            game_platform=random.choice(platforms),
            game_price=random.randint(5, 60)
        )

        # add and commit individually to get IDs back
        session.add(game)
        session.commit()

        games.append(game)

    reviews = []
    for game in games:
        for i in range(random.randint(1,5)):
            review = Review(
                review_score=random.randint(0, 10),
                review_comment=fake.sentence(),
                game_id=game.game_id
            )

            reviews.append(review)
    
    session.bulk_save_objects(reviews)
    session.commit()
    session.close()
