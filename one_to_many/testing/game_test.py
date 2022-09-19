from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Game, Review

class TestGame:
    '''Class Game in db.py'''

    # start session, reset db
    engine = create_engine('sqlite:///one_to_many/one_to_many.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # add test data
    mario_kart = Game(
        game_title="Mario Kart",
        game_platform="Switch",
        game_genre="Racing",
        game_price=60
    )

    session.add(mario_kart)
    session.commit()

    mk_review_1 = Review(
        review_score=10,
        review_comment="Wow, what a game",
        game_id=mario_kart.game_id
    )

    mk_review_2 = Review(
        review_score=8,
        review_comment="A classic",
        game_id=mario_kart.game_id
    )

    session.bulk_save_objects([mk_review_1, mk_review_2])
    session.commit()

    def test_game_has_correct_attributes(self):
        '''has attributes "game_id", "game_title", "game_platform", "game_genre", "game_price".'''
        assert(
            all(
                hasattr(
                    TestGame.mario_kart, attr
                ) for attr in [
                    "game_id",
                    "game_title",
                    "game_platform",
                    "game_genre",
                    "game_price"
                ]))

    def test_has_associated_reviews(self):
        '''has two reviews with scores 10 and 8.'''
        assert(
            len(TestGame.mario_kart.reviews) == 2 and
            TestGame.mario_kart.reviews[0].review_score == 10 and
            TestGame.mario_kart.reviews[1].review_score == 8
        )

    def test_can_add_new_review(self):
        '''can add new reviews'''
        
