
import sys
from .circle import CircleFromMircoRNA, CircleFromSeq
from .database import KmerDatabase
from .kmer import gc, homopolymer, split_kmer
from .logger import logger
from .util import green, red

class Primer:

    def __init__(
        self,
        short_kmer_size=16,
        long_kmer_size=20,
        kmer_count_per_circle_where_seq=5,
        kmer_count_per_circle_where_mircoRNA = 4,
        is_microRNA=False,
    ):

        assert long_kmer_size >= short_kmer_size
        self.short_kmer_size = short_kmer_size
        self.long_kmer_size = long_kmer_size
        self.kmer_delta = long_kmer_size - short_kmer_size
        self.is_microRNA = is_microRNA
        self.similar_kmer = []
        self.database=  KmerDatabase()
        self.circle_handle = (
            CircleFromSeq(
                self.database, 
                kmer_count_per_circle_where_seq, 
                short_kmer_size,
                long_kmer_size
            ),
            CircleFromMircoRNA(
                self.database,
                kmer_count_per_circle_where_mircoRNA,
                short_kmer_size,
                long_kmer_size
            )
        )

    def enable_mircoRNA(self):
        self.is_microRNA = True

    def disable_mircoRNA(self):
        self.is_microRNA = False

    def choice_database(self, database):
        if type(database) is str:
            self.database.choice_database([database])
        elif isinstance(database, (tuple, list)):
            self.database.choice_database(database)
        else:
            raise TypeError('')
    
    def _filter_rna(self, seq_list):
        ret = []
        # 一般序列
        # 需要进行筛选，取出符合条件的long kmer
        for seq in seq_list:
            r = []
            long_kmers = []
            short_kmers = []
            for index, long_kmer in enumerate(split_kmer(seq, self.long_kmer_size)):
                short = []
                for short_kmer in split_kmer(long_kmer, self.short_kmer_size):
                    short.append(short_kmer)
                long_kmers.append((index, long_kmer))
                short_kmers.extend(short)

            short_kmers = set(short_kmers)
            query_result = self.database.batch_find(short_kmers)
            # 所有hit到的kmer
            new_query_result = []
            for kmer, hit_database in query_result.items():
                if hit_database:
                    new_query_result.append(kmer)
            # 选择符合条件的long_kmer
            for index, long_kmer in long_kmers:
                yes = True
                for short in split_kmer(long_kmer, self.short_kmer_size):
                    # 检查gc和homopolymer的情况
                    if not gc(short) or not homopolymer(kmer):
                        yes = False
                        break
                    if short in new_query_result:
                        yes = False
                        break
                if yes:
                    r.append((index, long_kmer))
            ret.append(r)
        return self.circle_handle[0]([ret, None])

    def _filter_microrna(self, seq_list):
        # mircoRNA只筛选和数据库中哪些kmer相似
        # 不需要对序列的合法性进行评估
        short_kmers = []
        copy_seq_list = []
        for seq in seq_list:
            if len(seq) > 40:
                logger.warn(red('The seq<length: %d> is so long that it is not a microRNA.') % len(seq))
                continue
            short_kmers.extend(list(split_kmer(seq, self.short_kmer_size)))
            copy_seq_list.append(seq)
        query_result = self.database.batch_find(short_kmers)
        return self.circle_handle[1]([query_result, copy_seq_list])

    def filter_kmer(self, seq_list):
        if not self.database.list_active_database():
            logger.error(red('You must choice at least one database.'))
            exit()
        logger.info('Using database: [%s].' % green(', '.join(self.database._using_database)))
        if self.is_microRNA:
            return self._filter_microrna(seq_list)
        else:
            return self._filter_microrna(seq_list)

    def print_env(self):
        from .config import DEFAULT_GC, DEFAULT_KMER_SIZE, DEFAULT_MAX_HOMOPOLYMER_LENGTH
        logger.info('kmer_size  : %s' % green(DEFAULT_KMER_SIZE))
        logger.info('gc_content : [%s]' % green(', '.join([str(i) for i in DEFAULT_GC])))
        logger.info('homopolymer: %s' % green(DEFAULT_MAX_HOMOPOLYMER_LENGTH))
