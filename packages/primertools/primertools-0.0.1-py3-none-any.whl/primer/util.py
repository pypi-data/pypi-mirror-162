
import sys
from functools import lru_cache


def green(msg):
    return "\033[32m%s\033[0m" % str(msg)

def red(msg):
    return "\033[31m%s\033[0m" % str(msg)

def reverse_complement(sequence):
    reverse_dict = {
        'G':'C',
        'C':'G',
        'A':'T',
        'T':'A'
    }
    if 'U' in sequence:
        reverse_dict.update({
            'A':'U',
            'U':'A'
        })
    sequence = sequence[::-1]
    return ''.join([reverse_dict[base] for base in sequence])

map_dict = [0, 1, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 4, 1, 4, 4, 4, 2,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 0, 4, 1, 4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
u32_mask = (1 << 32) - 1

@lru_cache(1024 * 100)
def str2number_u32(s):
    number = 0
    for i in s:
        number <<= 2
        number |= map_dict[ord(i)]
    return number & u32_mask

import gzip


def decompress(path):
    return gzip.open(path, mode='rb', compresslevel=9).read()

def compress(path):
    with open(path, 'rb') as fp:
        data = fp.read()
    
    with open(path, 'wb') as fp:
        fp.write(gzip.compress(data, compresslevel=9))

def print_database(dbs):
    print(green('********************************'), file=sys.stderr)
    print('All avail database as follwing: ', file=sys.stderr)
    if dbs:
        for index, db in enumerate(dbs, start=1):
            print('%2d * %s' % (index, green(db)), file=sys.stderr)
    else:
        print(red(
            'None of database was found.'
            'Please run "primer create" to make a custom database.'
        ),file=sys.stderr)
    print(green('********************************'),file=sys.stderr)


def compute_gc(kmer):
    gc_count = 0
    for s in kmer:
        if s == 'G' or s == 'C':
            gc_count += 1
    return gc_count / len(kmer)
