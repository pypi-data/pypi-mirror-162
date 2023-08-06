import os

from cbitmap import UINT32_MAX, Bitmap

from .config import DEFAULT_KMER_SIZE, database_default_path
from .logger import logger
from .util import compress

map_dict = {
    'A':0,
    'G':1,
    'C':2,
    'U':3
}

mask = (1 << 32) - 1

def set_n(args):
    db , n = args
    db.set(n & mask)

def create(s, name, kmer_size=DEFAULT_KMER_SIZE, is_compress=True):
    db = Bitmap((1 << (kmer_size * 2)) - 1)
    logger.info('Create database: %s' % str(name))
    for index, seq in enumerate(s, start=1):
        seq = seq.upper()
        logger.info('Processing: %d, len: %d' % (index, len(seq)))
        db.set_kmers(seq, kmer_size)

    path = os.path.join(database_default_path, name + '.db')
    db.dump(path)
    logger.info('Database: %s created!' % str(name))
    if is_compress:
        compress(path)
        logger.info('Database: %s compressed!' % str(name))
