import os

DEFAULT_KMER_SIZE = 16
DEFAULT_GC = [0.4, 0.6]
DEFAULT_MAX_HOMOPOLYMER_LENGTH = 4
database_default_path = os.path.join(os.path.dirname(__file__), 'database')
if not os.path.exists(database_default_path):
    os.makedirs(database_default_path)

def _change(key, value):
    globals()['key'] = value


def change_kmersize(kmer_size):
    _change('DEFAULT_KMER_SIZE', kmer_size)


def change_gc(content):
    _change('DEFAULT_GC', content)


def change_homopolymer(length):
    _change('DEFAULT_MAX_HOMOPOLYMER_LENGTH', length)
