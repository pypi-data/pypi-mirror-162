from .config import DEFAULT_GC, DEFAULT_KMER_SIZE, DEFAULT_MAX_HOMOPOLYMER_LENGTH


def split_kmer(seq, kmer_size):
    for i in range(len(seq) - kmer_size + 1):
        yield seq[i:i+kmer_size]


def gc(kmer, gc_content=DEFAULT_GC):
    """ 检查kmer的gc含量

    - 符合content条件 返回 True
    - 不符合 返回 False
    """
    gc_count = 0
    for s in kmer:
        if s == 'G' or s == 'C':
            gc_count += 1
    compute_gc_content = gc_count / len(kmer)
    return compute_gc_content >= gc_content[0] and compute_gc_content <= gc_content[1]


def homopolymer(kmer, min_homo_length=DEFAULT_MAX_HOMOPOLYMER_LENGTH):
    """ 检查kmer中是否存在给定长度lemgth的homopolymer

        - 不存在 返回True
        - 存在 返回False
    """
    for i in range(len(kmer) - min_homo_length + 1):
        subkmer = kmer[i:i+min_homo_length]
        if len(set(subkmer)) == 1:
            return False
    return True
