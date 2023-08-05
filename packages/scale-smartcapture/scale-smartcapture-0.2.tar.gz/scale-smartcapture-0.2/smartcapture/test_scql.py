from .scql import SCQLPredicate


# TODO: add tests for AND shortcut, autotags, end to end triggers with refresh period
def test_basic_query():
    state = {
        "direction": "North",
        "speed": 30,
    }
    query = SCQLPredicate(
        {"$and": [{"direction": {"$eq": "North"}}, {"speed": {"$gt": 25}}]}, {}
    )
    assert query.evaluate(state)
    query = SCQLPredicate(
        {"$and": [{"direction": {"$eq": "North"}}, {"speed": {"$lt": 25}}]}, {}
    )
    assert not query.evaluate(state)
    query = SCQLPredicate(
        {"$not": {"$and": [{"direction": {"$eq": "North"}}, {"speed": {"$gt": 25}}]}},
        {},
    )
    assert not query.evaluate(state)


def test_nested_query():
    state = {
        "direction": "North",
        "speed": 30,
        "horn": True,
    }
    query = SCQLPredicate(
        {
            "$and": [
                {"$and": [{"direction": {"$eq": "North"}}, {"speed": {"$gt": 25}}]},
                {"horn": {"$eq": True}},
            ]
        },
        {},
    )
    assert query.evaluate(state)


def test_shortcut_and_query():
    state = {
        "direction": "North",
        "speed": 30,
    }
    query = SCQLPredicate(
        {"direction": {"$eq": "North"}, "speed": {"$gt": 25}}, {}
    )
    assert query.evaluate(state)
