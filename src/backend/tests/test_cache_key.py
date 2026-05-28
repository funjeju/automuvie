from app.repositories.cache_repository import make_cache_key


def test_same_input_same_key():
    a = make_cache_key("lyrics", genre="g", mood="m", prompt="p", duration=60, seed=None)
    b = make_cache_key("lyrics", genre="g", mood="m", prompt="p", duration=60, seed=None)
    assert a == b


def test_seed_changes_key():
    a = make_cache_key("lyrics", genre="g", mood="m", prompt="p", duration=60, seed=1)
    b = make_cache_key("lyrics", genre="g", mood="m", prompt="p", duration=60, seed=2)
    assert a != b


def test_stage_isolates_keys():
    a = make_cache_key("lyrics", genre="g", mood="m", prompt="p", duration=60)
    b = make_cache_key("music", genre="g", mood="m", prompt="p", duration=60)
    assert a != b
