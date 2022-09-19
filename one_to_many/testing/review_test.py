from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Game, Review

class TestReview:
    '''Class Review in db.py'''

    # start session, reset db
    engine = create_engine('sqlite:///one_to_many/one_to_many.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # add test data
    skyrim = Game(
        game_title="The Elder Scrolls V: Skyrim",
        game_platform="PC",
        game_genre="Adventure",
        game_price=20
    )

    session.add(skyrim)
    session.commit()

    skyrim_review = Review(
        review_score=10,
        review_comment="Wow, what a game",
        game_id=skyrim.game_id
    )

    session.add(skyrim_review)
    session.commit()

    def test_game_has_correct_attributes(self):
        '''has attributes "review_id", "review_score", "review_comment", "game_id".'''
        assert(
            all(
                hasattr(
                    TestReview.skyrim_review, attr
                ) for attr in [
                    "review_id",
                    "review_score",
                    "review_comment",
                    "game_id",
                ]))

    def test_knows_about_associated_game(self):
        '''has attribute "game" that is the "Game" object associated with its game_id.'''
        assert(
            TestReview.skyrim_review.game == TestReview.skyrim
        )
