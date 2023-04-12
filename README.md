# One-to-One and One-to-Many Relationships

## Learning Goals

- Use SQLAlchemy to join tables with one-to-one, one-to-many, and
  many-to-many relationships.

***

## Introduction

We already know that we can build our SQL tables such that they associate with
one another via **primary keys** and **foreign keys**. We can also use
SQLAlchemy to access data across different tables by establishing relationships
in code, without having to write tons of code ourselves, following the idea of
**convention over configuration**.

SQLAlchemy relationships make it easy to establish relationships between our
models, without having to write a ton of SQL ourselves. Sounds great, right? Now
that we have you totally hooked, let's take a look at how we use these SQLAlchemy
relationships.

Before we begin, run `pipenv install; pipenv shell` to generate and enter
your virtual environment. This will install `sqlalchemy`, `alembic`, `faker`,
`pytest`, and `ipdb`.

***

## How do we use SQLAlchemy Relationships?

SQLAlchemy ORM uses a `ForeignKey` column to constrain and join data models,
as well as a `relationship()` method that provides a property to one model
that can be used to access its related model. SQLAlchemy ORM also uses a
`backref()` method to create the property in the related model. This makes the
syntax for accessing related models and creating join tables very simple.

### One-to-Many Example

Here is some code that you might use to create a relationship between an order
and a customer:

```py
# example

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer(), primary_key=True)

    orders = relationship('Order', backref='customer')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer(), primary_key=True)
    customer_id = Column(Integer(), ForeignKey('customers.id'))
```

We can see that the `Customer` model contains an `orders` class attribute
that is set by the `relationship()` method. The `backref()` method therein
sets the reverse many-to-one relationship that **ref**ers **back** from the
`Order` model. Inclusion of a foreign key for a `Customer` instance in the
`Order` model is all that is needed to complete this relationship.

The `backref` goes into the **"one"** of the "one-to-many" relationship, as the
"one" is a single model object and does not need any additional arguments to
tell SQLAlchemy that it is something more specific like a list or dictionary.

(If you don't think you'll need the many-to-one relationship, you can
leave out the `backref`.)

### One-to-One Example

One-to-one relationships aren't _tremendously_ common, but they are simple
to build in SQLAlchemy ORM if you need to!

Let's say that orders have a lot of important associated data, but only two
or three columns' worth of regularly-queried data. In designing a database to
return data quickly, it makes the most sense for us to separate the important
attributes into a smaller table and create a one-to-one relationship with the
beefier database for metadata.

```py
# example

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer(), primary_key=True)

class OrderMetadata(Base):
    __tablename__ = 'orders_metadata'

    id = Column(Integer(), primary_key=True)
    order_id = Column(Integer(), ForeignKey("orders.id"))
    
    order = relationship('Order',
        backref=backref('order_metadata', uselist=False))
```

The syntax for a one-to-one relationship is identical to that of a one-to-many
relationship, with the exception that the `backref()` method takes
`uselist=False` as an optional second parameter. This means exactly what it
sounds like: the `Order` model refers back to the `OrderMetadata` model via a
property `order_metadata` that is not a list. (If it were a list, it would be
many!)

***

## Overview

In this lesson, we'll be building out a **one-to-many** relationship between two
models: **games** and **reviews**. We'll set up our database so that a game
**has many** reviews, and each review **belongs to** a specific game.

By writing a few migrations and making use of the appropriate SQLAlchemy
methods, we'll be able to:

- Ask a game about its reviews.
- Ask a review about its game.

Here's what our Entity Relationship Diagram (ERD) looks like:

![Game Reviews ERD](https://curriculum-content.s3.amazonaws.com/phase-3/active-record-associations-one-to-many/games-reviews-erd.png)

***

## Building our Migrations

### The Game Model

A game will _have many_ reviews. Before we worry about the migration that will
implement this in our reviews table, let's think about what that table will look
like:

|  id  |     title     |  platform  |  platform   | price |
| --------- | ------------------ | --------------- | ---------------- | ---------- |
|     1     | Breath of the Wild |      Switch     | Action-adventure |     60     |

Our games table doesn't need any information about the reviews, so it makes
sense to generate this table first: it doesn't have any dependencies on another
table. This makes sense even thinking about our domain in the real world: a game
can exist without any reviews.

The basic structure for your SQLAlchemy app is already configured. Navigate to
the `lib/` directory and you should see the following directory
structure:

```console
.
├── alembic.ini
├── debug.py
├── migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 0d06d41c7860_initialize_database.py
├── models.py
├── one_to_many.db
├── seed.py
└── testing
    ├── conftest.py
    ├── game_test.py
    └── review_test.py
```

`alembic.ini` points to a SQLite database called `one_to_many.db`. The models
should go into `models.py`; it is already configured to create a `Base`, and
`env.py` is pointing to its metadata.

We made another change to `env.py` to support the addition of foreign keys on
line 69:

```py
connection=connection, target_metadata=target_metadata, render_as_batch=True,
```

SQLite presents a challenge to migration tools as it does not support `ALTER`
statements, which relational databases frequently rely upon.

To help solve this problem, Alembic provides the batch operations context.
With batch operations, a table is named, and then a series of changes
to that table are specified. When the batch is complete, a process begins
where the existing table structure is copied from the database, a new version
of this table is created with the desired changes, data is copied from the old
table to the new table, and the old table is dropped and the new one renamed to
the original name.

Just remember that alterations to tables require `render_as_batch=True` in
`env.py` from the start of your first migration.

Run `alembic upgrade head` to create your database.

Navigate to `lib/models.py` and build a basic model for the `games` table:

```py
# models.py

from sqlalchemy import ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)
    title = Column(String())
    genre = Column(String())
    platform = Column(String())
    price = Column(Integer())

```

Note that we've added a `convention` and `metadata` to our models. SQLite
requires names for changes to foreign keys (we'll talk about these shortly)
and several other fields in models. Our `convention` provides a template for
naming these changes, and `metadata` saves them to a `sqlalchemy.MetaData`
object. Passing this to our `declarative_base` object allows Alembic to generate
these names automatically when we autogenerate migrations.

Run `alembic revision --autogenerate -m'Create Game Model'` from inside of the
`lib/` directory. You should see the following output:

```console
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'games'
  Generating ...python-p3-sqlalchemy-one-to-many/one-to-many/migrations/versions/62797912f786_create_model.py ...  done
```

Run `alembic upgrade head` to generate a database with your `Game` model.

### The Review Model

A review will **belong to** a specific game. What does that mean in terms of our
database? Think back to what you learned about SQL and joining between multiple
tables. How can we connect between a review and its associated game?

That's right, we need a **foreign key**! Since a review belongs to a specific
game, we need some way of indicating on the review _which_ specific game it
belongs to.

Let's take a look at what our `reviews` table will need to look like:

| id  | score | comment | id |
| ---------- | ------------ | -------------- | ------- |
|     1      |      10      |   A classic!   |    1    |

Ok! Now that we know what we need to create, let's head back to `models.py`
and write out a new model:

```py
# models.py

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer(), primary_key=True)
    score = Column(Integer())
    comment = Column(String())
    game_id = Column(Integer(), ForeignKey('games.id'))
```

Make sure to add the relationship to `Game` as well:

```py
# models.py

class Game(Base):
    
    # tablename, columns

    reviews = relationship('Review', backref=backref('game'))

```

Lastly, don't forget to set the `__repr__()` for each of your models. You''ll
thank me later!

```py
# models.py

class Game(Base):
    
    # tablename, columns, relationship

    def __repr__(self):
        return f'Game(id={self.id}, ' + \
            f'title={self.title}, ' + \
            f'platform={self.platform})'

class Review(Base):
    
    # tablename, columns, relationship

    def __repr__(self):
        return f'Review(id={self.id}, ' + \
            f'score={self.score}, ' + \
            f'game_id={self.game_id})'
```

Great! Now go ahead and run the same commands in your terminal to generate
and run our migrations:

```console
$ alembic revision --autogenerate -m'Add Review Model'
# => INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# => INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
# => INFO  [alembic.autogenerate.compare] Detected added table 'reviews'
# =>   Generating ...sqlalchemy-relationships/python-p3-sqlalchemy-one-to-many/lib/migrations/versions/1f2ce6b5977d_add_model.py ...  done

$ alembic upgrade head
# => INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
# => INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
# => INFO  [alembic.runtime.migration] Running upgrade 62797912f786 -> 1f2ce6b5977d, Add Review Model
```

There is also some code in the `seed.py` file that we'll use to generate
some data for our two models. In the seed file, we first create a game instance,
then use the ID from that game instance to associate it with the corresponding
review. The data itself is generated automatically using `faker`.

Run this to fill the database with games and reviews:

```console
$ python seed.py
```

***

## Exploring our Relationships Using SQLAlchemy

### A Review Belongs to a Game

Let's enter the Python shell and access the first review. Run `python
debug.py` to set up a session and import the data models:

```py
# Access the first review instance in the database
review = session.query(Review).first()
review
# => Review(id=1, score=7, game_id=1)

# Get the game_id foreign key for the review instance
review.game_id
# => 1
```

We know that this review has some relationship to data in the `games` table. We
could even use the foreign key to access that data directly:

```py
# Find a specific game instance using an ID
session.query(Game).filter_by(id=review.game_id).first()
# => Game(id=1, title=Jacob Floyd, platform=wii u)
```

But SQLAlchemy provides an even easier route to the related game:

```py
review.game
# => Game(id=1, title=Jacob Floyd, platform=wii u)
```

_Nice!_

### A Game Has Many Reviews

Now let's access the first game:

```py
game = session.query(Game).first()
game
# => Game(id=1, title=Jacob Floyd, platform=wii u)
```

As expected, this is the same game that we found through the first review. We
can search for reviews using this game's ID as a filter:

```py
reviews = session.query(Review).filter_by(game_id=game.id)
[review for review in reviews]
# => [Review(id=1, score=7, id=1), Review(id=2, score=7, id=1), Review(id=3, score=8, id=1)]
```

But just as with finding the game for a review, we can access a game's reviews
directly using its relationship:

```py
game.reviews
# => [Review(id=1, score=7, game_id=1), Review(id=2, score=7, game_id=1), Review(id=3, score=8, game_id=1)]
```

***

## Cascades

In most **belongs to** relationships like we see here with reviews and games,
we want to make sure that when the parent disappears, the child does as well.
SQLAlchemy handles this logic with **cascades**.

A cascade is a behavior of a SQLAlchemy relationship that carries from parents
to children. _All SQLAlchemy relationships have cascades_. By default, a
relationship's cascade behavior is set to `'save-update, merge'`. This can be
changed to any combination of a set of behaviors:

- `save-update`: when an object is placed into a session with `Session.add()`,
  all objects associated with it should also be added to that same session.
  - _If a game is added to a session, all of its reviews will be as well._
- `merge`: if the session contains duplicate objects, `merge` eliminates those
  duplicates.
  - _If a game is merged to a session, its reviews that have already
    been added to the session will not be added again._
- `delete`: when a parent is deleted, its children are deleted as well.
  - _If a game is deleted, its reviews will be deleted as well._
- `all`: a combination of `save-update`, `merge`, and `delete`.
- `delete-orphan`: when a child is disassociated from its parent, it is deleted.
  - _If a review is removed from `game.reviews`, the review will be deleted._

### Configuring a `Game`/`Review` Cascade

As we begin configuring our cascade, let's ask ourselves a few questions:

1. Do we need reviews to be updated when their parent games are updated?
2. Do we need to avoid adding duplicate reviews to our session?
3. Do we need to delete reviews when their parent games are deleted?
4. Do we need to delete reviews when they are no longer associated with games
   (i.e. orphaned)?

We know that we want reviews to be associated with their parent games, so that's
a "yes" to number 1. We also want to avoid adding duplicates to the session, so
that's a "yes" to 2 as well.

Reviews are inherently linked to games, so we should delete them if the games
no longer exist. That's a "yes" to number 3.

Since we are going to be using `save-update`, `merge`, and `delete`, we can
start our cascade with `all`.

```py
reviews = relationship('Review', backref=backref('game'), cascade='all')
```

Lastly, for the same reason we included `delete`, we _do_ want to delete reviews
that are no longer associated with games. What good is a review of nothing?
Let's say "yes" to number 4 as well and finish our cascade:

```py
reviews = relationship('Review', backref=backref('game'), cascade='all, delete-orphan')
```

Our database is now configured to delete reviews when their parent games are
deleted and when they are removed from their parent game, or orphaned.

***

## Conclusion

In this lesson, we explored the most common kind of relationship between two
models: the **one-to-many** or "has-many"/"belongs-to" relationship. With a
solid understanding of how to connect databases using primary and foreign keys,
we can take advantage of some helpful SQLAlchemy methods that make it much
easier to build comprehensive database schemas and integrate them into our
Python applications.

Run `pytest -x` to make sure all of the tests are passing. In the next lesson,
we'll explore many-to-many relationships in SQLAlchemy

***

## Solution Code

```py
from sqlalchemy import ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer(), primary_key=True)
    title = Column(String())
    genre = Column(String())
    platform = Column(String())
    price = Column(Integer())

    reviews = relationship('Review', backref=backref('game'), cascade='all, delete-orphan')

    def __repr__(self):
        return f'Game(id={self.id}, ' + \
            f'title={self.title}, ' + \
            f'platform={self.platform})'

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer(), primary_key=True)
    score = Column(Integer())
    comment = Column(String())
    
    game_id = Column(Integer(), ForeignKey('games.id'))

    def __repr__(self):
        return f'Review(id={self.id}, ' + \
            f'score={self.score}, ' + \
            f'game_id={self.game_id})'

```

***

## Resources

- [Python 3.8.13 Documentation](https://docs.python.org/3/)
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/en/14/orm/)
- [Alembic 1.8.1 Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [Basic Relationship Patterns - SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html)
- [Running “Batch” Migrations for SQLite and Other Databases](https://alembic.sqlalchemy.org/en/latest/batch.html)
