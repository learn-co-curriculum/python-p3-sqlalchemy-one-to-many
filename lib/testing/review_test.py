from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conftest import SQLITE_URL
from models import Game, Review

class TestReview:
    '''Class Review in models.py'''

    # start session, reset db
    engine = create_engine(SQLITE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # add test data
    skyrim = Game(
        title="The Elder Scrolls V: Skyrim",
        platform="PC",
        genre="Adventure",
        price=20
    )

    session.add(skyrim)
    session.commit()

    skyrim_review = Review(
        score=10,
        comment="Wow, what a game",
        game_id=skyrim.id
    )

    session.add(skyrim_review)
    session.commit()

    def test_game_has_correct_attributes(self):
        '''has attributes "id", "score", "comment", "game_id".'''
        assert(
            all(
                hasattr(
                    TestReview.skyrim_review, attr
                ) for attr in [
                    "id",
                    "score",
                    "comment",
                    "game_id",
                ]))

    def test_knows_about_associated_game(self):
        '''has attribute "game" that is the "Game" object associated with its game_id.'''
        assert(
            TestReview.skyrim_review.game == TestReview.skyrim
        )
