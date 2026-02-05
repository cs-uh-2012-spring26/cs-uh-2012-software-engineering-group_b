from app.db.constants import ID


def exclude_keys(item: dict, keys_to_exclude: set):
    """
    Remove specified keys from an item.
    """
    return {k: v for k, v in item.items() if k not in keys_to_exclude}

def assert_items_equal(actual, expected):
    """
    Assert two items are equal, ignoring '_id'.
    """
    assert exclude_keys(actual, {ID}) == exclude_keys(expected, {ID})
