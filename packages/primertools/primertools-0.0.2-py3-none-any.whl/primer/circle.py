
from .kmer import gc, homopolymer, split_kmer
from .logger import logger
from .util import compute_gc, reverse_complement


class CircleBase:
    """ kmer成环 """

    def __init__(
        self,
        database,
        kmer_count_per_circle,
        short_kmer_size,
        long_kmer_size
    ):
        self.database = database
        self.kmer_count_per_circle = kmer_count_per_circle
        self.short_kmer_size = short_kmer_size
        self.long_kmer_size = long_kmer_size
        kmer_delta = long_kmer_size - short_kmer_size
        self.check_range = slice(kmer_delta+1, kmer_delta+2*short_kmer_size-1)
        # self.check_range1 = slice(kmer_delta+1, kmer_delta+2*short_kmer_size-1)
        # self.check_range2 = (slice(-self.short_kmer_size+1, None),slice(0, self.short_kmer_size-1))
        self.check_kmer_count = short_kmer_size - 1
        self.circle = []

    def check_circle(self):
        short_kmers = []
        subcircle = []
        for circle in self.circle:
            c = circle[self.check_range]
            subcircle.append(c)
            short_kmers.extend(list(split_kmer(circle[self.check_range], self.short_kmer_size)))

        return self.database.batch_find(short_kmers), subcircle

    def reverse_circle(self):
        self.circle = [
            reverse_complement(circle)
            for circle in self.circle
        ]
        return self

    def __iter__(self):
        return iter(self.circle)

    def is_empty(self):
        return len(self.circle) > 0

    def __len__(self):
        return len(self.circle)

    def __call__(self, ret):
        raise NotImplementedError()

class CircleFromMircoRNA(CircleBase):

    def __str__(self):
        return '<CircleFromMircoRNA>'

    def __call__(self, ret):
        query_result, raw = ret
        self.report = [set() for _ in range(len(raw))]
        self.circle = []
        for index, seq in enumerate(raw):
            for short_kmer in split_kmer(seq, self.short_kmer_size):
                if query_result[short_kmer]:
                    self.report[index].update(query_result[short_kmer])

            self.circle.append(
                ''.join(
                    [seq for i in range(self.kmer_count_per_circle)]
                )
            )

        check_ret, subcircle = self.check_circle()
        for index, sub_seq in enumerate(subcircle):
            for short_kmer in split_kmer(sub_seq, self.short_kmer_size):
                if sub_seq in check_ret:
                    self.report[index].update(check_ret[sub_seq])

        self.circle = [reverse_complement(circle) for circle in self.circle]
        return self

    def to_txt(self, path):
        with open(path, 'w', encoding='utf-8') as fp:
            for index, circle in enumerate(self.circle):
                fp.write('%s\t%.3f\t%s\n' % (circle, compute_gc(circle), ','.join(self.report[index])))

class CircleFromSeq(CircleBase):

    def __str__(self):
        return '<CircleFromSeq>'

    @staticmethod
    def get_hit_range(pos):
        if not pos:
            return []
        prev_pos = pos[0]
        p = []
        pos_group = [prev_pos]
        for pos in pos[1:]:
            if prev_pos+1 == pos:
                pos_group.append(pos)
            else:
                p.append([i for i in pos_group])
                pos_group =[pos]
            prev_pos = pos
        else:
            p.append([i for i in pos_group])
        return p

    def __call__(self, ret):
        query_result, _ = ret
        # 首先，分析hit的位置信息
        pos = [[i[0] for i in j] for j in query_result]
        pos_range = [self.get_hit_range(p) for p in pos]
        return self

    def choose_kmer(self):
        pass

    def test_circle_with_circle(self):
        pass
