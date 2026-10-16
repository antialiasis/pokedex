""" pokedex.defaults - logic for finding default paths """

import os

def get_default_db_uri_with_origin():
    uri = os.environ.get('POKEDEX_DB_ENGINE', None)
    origin = 'environment'

    if uri is None:
        from importlib.resources import files
        sqlite_path = files('pokedex').joinpath('data/pokedex.sqlite')
        uri = 'sqlite:///' + sqlite_path
        origin = 'default'

    return uri, origin

def get_default_index_dir_with_origin():
    index_dir = os.environ.get('POKEDEX_INDEX_DIR', None)
    origin = 'environment'

    if index_dir is None:
        from importlib.resources import files
        index_dir = files('pokedex').joinpath('data/whoosh-index')
        origin = 'default'

    return index_dir, origin

def get_default_csv_dir_with_origin():
    from importlib.resources import files
    csv_dir = files('pokedex').joinpath('data/csv')
    origin = 'default'

    return csv_dir, origin


def get_default_db_uri():
    return get_default_db_uri_with_origin()[0]

def get_default_index_dir():
    return get_default_index_dir_with_origin()[0]

def get_default_csv_dir():
    return get_default_csv_dir_with_origin()[0]


