from .edge import Edge
import sys

signal_value = False

class Node:
    def __init__(self, node_id=-1):
        super().__init__()
        self.node_id = node_id
        self.value = []
        self.label = []
        self.in_edge = Edge()
        self.out_edge = Edge()

    @property
    def in_degree(self):
        return len(self.in_edge)

    @property
    def out_degree(self):
        return len(self.out_edge)

    def add(self, value, label):
        self.value.append(value)
        self.label.append(label)
    
    def add_in_edge(self, node_id):
        self.in_edge.add(node_id)
    
    def add_out_edge(self, node_id):
        self.out_edge.add(node_id)
    
    def debug_link_str(self):
        sys.stderr.write(
            'in: [%s] - [%d|%s] - out: [%s]\n' % (
                ','.join([str(i) for i in self.in_edge]) or str(-1),
                self.node_id,
                ','.join([str(i) for i in self.value]),
                ','.join([str(i) for i in self.out_edge]) or str(-1),
            )
        )

    def debug_str(self):
        sys.stderr.write(
            '%s' % ','.join([str(i) for i in self.value]),
        )

    if signal_value:
        def __str__(self):
            return '%s' % ','.join([str(i) for i in self.value])
    else:
        def __str__(self):
            return '%s' % ','.join([str(i[-1]) for i in self.value])

    def __len__(self):
        return len(self.value)
