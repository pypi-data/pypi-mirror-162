from .node import Node
import numpy as np

class Seq:

    def __init__(self, seq, label):
        self.seq = seq
        self.label = label

    def __iter__(self):
        return iter(self.seq)

    def __len__(self):
        return len(self.seq)

    def __getitem__(self, index):
        return self.seq[index]

    def to_nodes(self):
        nodes = []
        # create
        for (index, s) in enumerate(self.seq):
            node = Node(index)
            node.add(s, self.label)
            nodes.append(node)
        # link
        head = nodes[0]
        for node in nodes[1:]:
            head.add_out_edge(node.node_id)
            node.add_in_edge(head.node_id)
            head = node
        return nodes

    def stdv(self):
        seq = np.array(self.seq, dtype=np.float)
        return Seq((seq - seq.mean()) / seq.std(), self.label)

    def __str__(self):
        return '%s\n%s' % (self.label, self.seq)

class SeqFileIter:

    def __init__(self, path):
        self.path = path
        self._iter_data = self._read()

    def _read(self):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self._iter_data)

    def __getitem__(self, index):
        return self._iter_data[index]

    def __len__(self):
        return len(self._iter_data)

    def __str__(self):
        return '\n'.join([str(s) for s in self._iter_data])

class Fasta(SeqFileIter):

    def _read(self):
        data = []
        label = ''
        seq = ''
        with open(self.path, 'r', encoding='utf-8') as fp:
            for line in fp:
                if line.startswith('#'):continue
                line = line.strip('\n')
                if line.startswith('>'):
                    if seq:
                        data.append(Seq(seq, label))
                        seq = ''
                    label = line.strip('>')
                else:
                    seq += line.strip()
            data.append(Seq(seq, label))
        return data

from .alignment import (
    AlignmentSeq
)
def read_file(path, file_type='fasta'):
    if file_type == 'fasta':
        return Fasta(path), AlignmentSeq
