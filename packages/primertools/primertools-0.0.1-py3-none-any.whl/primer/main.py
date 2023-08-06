import argparse
import os

from .config import change_gc, change_homopolymer, change_kmersize
from .create_database import create
from .logger import logger
from .primer import Primer
from .seq import Seq
from .util import green, print_database


def make_args():

    arg = argparse.ArgumentParser()

    arg.add_argument('-k', '--kmer_size', type=int, help='kmer size', default=16)
    arg.add_argument('-g', '--gc', type=str, help='The GC content range', default='0.4,0.5')
    arg.add_argument('-p', '--poly', type=int, help='The max homopolymer length', default=3)

    subparser = arg.add_subparsers(title='help')
    arg.set_defaults(func=handle_default, parser=arg)

    list_db = subparser.add_parser('list', help='List all available database')
    list_db.set_defaults(func=handle_list_db, parser=list_db)

    db = subparser.add_parser('create', help='Create DB')
    db.add_argument('-f', '--file', help='sequence file')
    db.add_argument('-t', '--type',help='file type', default='fasta', choices=['fasta', 'fastaq'])
    db.add_argument('-n','--name', help='the name of database')
    # db.add_argument('-c', '--compress', action='store_true', default=False, help='compress kmer db or not')
    db.set_defaults(func=handle_db, parser=db)

    microrna = subparser.add_parser('microrna', help='MicroRNA primer design')
    microrna.add_argument('-f', '--file', help='sequence file')
    microrna.add_argument('-t', '--type',help='file type', default='fasta', choices=['fasta', 'fastaq'])
    microrna.add_argument('-c', '--count', default=4, type=int, help='per kmer in one circle')
    microrna.add_argument('-o', '--output', help='primer output')
    microrna.add_argument('-u', '--use', action='append', help='choose which database to use')
    microrna.set_defaults(func=handle_microRNA, parser=microrna)

    seq = subparser.add_parser('rna',help='RNA primer design')
    seq.add_argument('-f', '--file', help='sequence file')
    seq.add_argument('-t', '--type',help='file type', default='fasta', choices=['fasta', 'fastaq'])
    seq.add_argument('-n', '--number', type=int, help='The max number of primer')
    seq.add_argument('-c', '--count', default=4, type=int, help='per kmer in one circle')
    seq.add_argument('-o', '--output', help='primer output')
    seq.add_argument('-u', '--use', action='append', help='choose which database to use')
    seq.set_defaults(func=handle_RNA, parser=seq)
    return arg.parse_args()

def print_help(args):
    args.parser.print_help()
    exit(0)

def handle_default(args):
    print_help(args)

def args_check(args, arg_names):
    for arg in arg_names:
        if not getattr(args, arg):
            print_help(args)

def handle_list_db(args):
    p = Primer()
    print_database(p.database._all_database)

def create_db(file_path, file_format, kmer_size, db_name, compress):
    s = Seq(db_name)
    s.from_file(file_path, file_format)
    create(s, db_name, kmer_size, compress)

def handle_db(args):
    args_check(args, ['file', 'type', 'name'])
    create_db(args.file, args.type, args.kmer_size, args.name, False)

def handle_microRNA(args):
    args_check(args, ['file', 'type', 'output', 'use'])
    s = Seq('seq')
    if os.path.isfile(os.path.abspath(args.file)):
        s.from_file(args.file, args.type)
    else:
        s.from_seq(args.file.upper())
    p = Primer(is_microRNA=True,kmer_count_per_circle_where_mircoRNA=args.count)
    p.print_env()
    for d in args.use:
        p.database.use(d)
    ret = p.filter_kmer(s)
    ret.to_txt(args.output)
    logger.info('File save to %s' % green(os.path.abspath(args.output)))

def handle_RNA(args):
    # args_check(args, ['file', 'type', 'output', 'number', 'use'])
    # s = Seq('seq')
    # s.from_file(args.file, args.type)
    # p = Primer(kmer_count_per_circle_where_seq=args.count)
    # p.print_env()
    # for d in args.use:
    #     p.database.use(d)
    
    # ret = p.filter_kmer(s)
    print(green('Coming soon...'))


def run():
    args = make_args()
    change_gc([float(i) for i in args.gc.split(',')])
    change_homopolymer(args.poly)
    change_kmersize(args.kmer_size)
    args.func(args)
