from Bio.SeqIO import parse
from Bio.Seq import Seq as _Seq
import gzip

class Seq:

    def __init__(self, name):
        self.name = name
        self.seq = []

    def read_fasta(self, fasta_path, file_type):
        if fasta_path.lower().endswith('gz'):
            fasta_path = gzip.open(fasta_path, 'r')
        f = parse(fasta_path, file_type)
        for seq in f:
            yield None, seq.seq

    def from_seq(self, seq):
        seq = _Seq(seq).transcribe()
        self.seq.append(str(seq))

    def from_file(self, path, file_type):
        self.seq.append((seq.transcribe() for _, seq in self.read_fasta(path, file_type)))

    def __iter__(self):
        for s in self.seq:
            if type(s) is str:
                s = [s]
            for _s in s:
                yield str(_s)

    def __len__(self):
        return len(self.seq)
