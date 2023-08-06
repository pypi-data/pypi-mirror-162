import sys

from .node import Node
from collections import OrderedDict
import pickle
import numpy as np

from functools import lru_cache

class GraphTo:

    def to_msa(self, output=sys.stdout):
        """ 输出到msa格式 """
        result = OrderedDict()
        for label in self.label:
            result[label] = ['-'] * len(self)
        for index, node in enumerate(self.nodes):
            for value_index, node_label in enumerate(node.label):
                result[node_label][index] = node.value[value_index]
        for label, alignment in result.items():
            output.write('%s\t%s\n' %
                         (str(label), ''.join([str(i) for i in alignment])))


    def to_json(self, output=sys.stdout):
        """ 将图节点转换为json格式，用来进行可视化 """
        nodes = [
            {"id": node.node_id, "label": str(node), "x": index}
            for index, node in enumerate(self.nodes)
        ]
        _edges = []
        for node in self.nodes:
            for in_edge in node.in_edge:
                _edges.append(
                    (in_edge, node.node_id, len(node))
                )
        edges = [
            {"from": e[0], "to": e[1], "arrows":"to"}
            for e in _edges
        ]
        import json
        s = json.dumps(
            {'nodes': nodes, 'edges': edges}
        )
        if output:
            output.write(s)
        else:
            return s

    def to_consense(self, output=sys.stdout):
        """ 生成一致性序列 """
        pass

    def to_html(self, output=sys.stdout):
        """ 输出为html可视化 """
        html = (
            '<!doctype html>'
            '<html>'
            '<head>'
            '<title>POA Graph Alignment</title>'
            '<script type="text/javascript" src="https://unpkg.com/vis-network@9.0.4/standalone/umd/vis-network.min.js"></script>'
            '</head>'
            '<body>'
            '<div id="loadingProgress">0%</div>'
            '<div id="mynetwork"></div>'
            '<script type="text/javascript">'
        )

        html += 'var data = %s;' % self.to_json(None)

        html += (
            "var container = document.getElementById('mynetwork');"
            "var options = {"
            " width: '100%',"
            "height: '1200px',"
            " physics: {"
            "stabilization: {"
            "updateInterval: 10,"
            "}"
            "}"
            "};"
            "var network = new vis.Network(container, data, options);"
            'network.on("stabilizationProgress", function (params) {'
            'document.getElementById("loadingProgress").innerText = Math.round(params.iterations / params.total * 100) + "%";'
            '});'
            'network.once("stabilizationIterationsDone", function () {'
            'document.getElementById("loadingProgress").innerText = "100%";'
            'setTimeout(function () {'
            'document.getElementById("loadingProgress").style.display = "none";'
            '}, 500);'
            '});'
            '</script>'
            '</body>'
            '</html>'
        )

        output.write(html)
        if not output.closed:
            output.close()


class GraphDumpLoad:

    def _dump_data(self):
        return {
            'nodes': self.nodes,
            'node_id2node_index': self.node_id2node_index,
            'node_id2node': self.node_id2node,
            'node_index2node_id': self.node_index2node_id,
            'node_id': self.node_id,
            'label': self.label
        }

    def dump(self, path):
        data = self._dump_data()
        with open(path, 'wb') as fp:
            fp.write(b'graph')
            fp.write(pickle.dumps(data))

    def load(self, path):
        with open(path, 'rb') as fp:
            if fp.read(5) == b'graph':
                data = fp.read()
                data = pickle.loads(data)
                for k,v in data.items():
                    setattr(self, k ,v)
            else:
                raise RuntimeError('文件内容错误')


class GraphMix(GraphDumpLoad, GraphTo):
    pass


class Graph(GraphMix):
    """ 有向无环图 """

    def __init__(self):
        self.nodes = []
        self.node_id2node = {}
        self.node_id2node_index = {}
        self.node_index2node_id = {}
        self.node_id = 0
        self.label = []

    def init_graph_by_seq(self, seq):
        self.label.append(seq.label)
        self.nodes = seq.to_nodes()
        self._update_hook()

    def _update_hook(self):
        """ 更新节点id和index的关系 """
        old_nodes_len = self.node_id
        new_nodes = self.nodes[old_nodes_len:]
        # 更新node id和node的映射字典
        new_node_id2node = {node.node_id: node for node in new_nodes}
        self.node_id2node.update(new_node_id2node)
        # 更新 node index和node id的映射字典
        new_node_index2node_id = {
            old_nodes_len + i: node.node_id
            for (i, node) in enumerate(new_nodes)
        }
        self.node_index2node_id.update(new_node_index2node_id)
        # 更新node id和node index的映射字典
        new_node_id2node_index = {
            v: k for k, v in new_node_index2node_id.items()
        }
        self.node_id2node_index.update(new_node_id2node_index)
        # 更新下一个插入的node id
        self.node_id = len(self.nodes)

    def _add_node(self, value, label):
        node = Node(self.node_id)
        node.add(value, label)
        self.nodes.append(node)
        self.node_id += 1
        # print('add: %s, node_id: %d' % (str(node), self.node_id))
        return node

    def _link_node(self, from_node, to_node):
        """ 连接两个节点 """
        if type(from_node) is int:
            from_node = self.node_id2node[from_node]
        if type(to_node) is int:
            to_node = self.node_id2node[to_node]
        from_node.add_out_edge(to_node.node_id)
        to_node.add_in_edge(from_node.node_id)

    def _topological_sort(self):
        """ 拓扑排序 Kahn算法"""
        nodes = self.nodes
        sorted_nodes = []
        # {id: in_degree}
        in_degree_node = {}
        for i in range(len(self)):
            # 全部完成排序
            if len(sorted_nodes) == len(nodes):
                break
            find = False
            one_loop_find_nodes = []
            for node in nodes:
                # 已经排序的节点直接跳过
                if node in sorted_nodes:
                    continue
                in_degree = node.in_degree
                # 查找入度为0的节点
                if (
                    in_degree == 0 or
                    in_degree == in_degree_node.get(node.node_id, -1)
                ):
                    one_loop_find_nodes.append(node)
                    find = True
            for node in one_loop_find_nodes:
                # 将该节点的out_edge对应的节点的入度减一
                for out in node.out_edge:
                    if out not in in_degree_node:
                        in_degree_node[out] = 1
                    else:
                        in_degree_node[out] += 1
            sorted_nodes += one_loop_find_nodes
            if not find:
                # for node in self:
                #     node.debug_link_str()
                raise RuntimeError('存在环，非DAG图')

        # 将图更新为重新排序的节点
        self.nodes = sorted_nodes
        # 设置为0，即全部更新
        self.node_id = 0
        self._update_hook()

    def _merge_seq_to_graph_by_traceback_result(self, matches, seq):
        """ 根据比对结果，将一条新的序列合并到图上 

            有两种情况
                - 比对上
                    - match 直接融合
                    - mismatch 直接融合
                - 没有比对上（gap），需要创建新节点，同时与图上的其他节点进行连接

            融合时，由于序列之间存在一个顺序关系，可以使用下面的方法进行融合

            - step1: 收集序列中所有节点所位于的节点（旧节点和新节点）
            - step2: 将收集的节点，按照顺序进行连接

            基于上面的分析，这里需要做两件事

            - 按照序列顺序进行创建新节点/融合节点
            - 节点连接
        """
        nodes = []
        # sort
        for index, s in enumerate(seq):
            if index in matches:
                node = self[matches[index]]
                node.add(s, seq.label)
            else:
                node = self._add_node(s, seq.label)
            nodes.append(node)

        # link
        for index in range(len(nodes)-1):
            self._link_node(nodes[index], nodes[index+1])

    def add_seq_to_align(self, alignment):
        """ 添加一条新的序列进行比对 """
        seq = alignment.seq
        if seq.label in self.label:
            return
        self.label.append(seq.label)
        matches = alignment.align()
        self._merge_seq_to_graph_by_traceback_result(matches, seq)
        self._topological_sort()

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __getitem__(self, index):
        return self.nodes[index]


class SegmentGraph(Graph):
    """ 输出分段信息 """
    status = True


    def load(self, path):
        data = pickle.load(open(path, 'rb'))
        if not data['status']:
            self.status = False
            return
        for k,v in data.items():
            if k == 'g':
                for gk, gv in data[k].items():
                    setattr(self, gk, gv)
                continue
            setattr(self, k , v)

    def to_segment(self, ground_truth):
        """ 输出segment之间的overlap """
        segment = OrderedDict()
        for label in self.label:
            segment[label] = [-1] * len(self)

        for index, node in enumerate(self):
            for node_label in node.label:
                segment[node_label][index] = 1

        for label in segment:
            segment[label] = np.nonzero(np.array(segment[label]) > 0)[0]

        ret = {}
        for label, segment_truth in ground_truth.items():
            ret[label] = np.split(segment[label], np.cumsum(np.array(segment_truth)))

        return ret

    def get_ground_truth(self):
        truth = OrderedDict()
        for label in self.label:
            truth[label] = []

        for index, fake in enumerate(self.fake):
            truth[self.label[index]] = [len(i) for i in fake]
        
        return truth

    def prepare_data(self, kmer_size=10):
        """ 准备评估所需的数据 """
        if not self.status:return
        ground_truth = self.get_ground_truth()
        s = self.to_segment(ground_truth)
        data = []
        truth = {}
        for label in self.label:
            one_label = ground_truth[label]
            one_label = np.cumsum(one_label)
            truth[label] = [[i for i in range(1, one_label[0])]]
            for index, _ in enumerate(one_label[:-1]):
                truth[label].append(
                    [i for i in range(one_label[index], one_label[index+1])]
                )
        for kmer_postion in range(kmer_size):
            one_postion = []
            one_postion_truth = []
            for index, label in enumerate(self.label):
                one_postion.extend(
                    s[label][kmer_postion]
                )
                one_postion_truth.extend(
                    truth[label][kmer_postion]
                )
            data.append((one_postion, one_postion_truth))
        return data

    @lru_cache
    def prepare_data2(self):
        """准备每一条序列中每个元素与节点id的关系
        {
            node_id:{
                seq_id:index
            }
        }
        
        """

        seqs_index_count = {}
        seqs_id = {}
        for label in self.label:
            seqs_index_count[label] = 0

        for node in self.nodes:
            seqs_id[node.node_id] = {}
            for node_label in node.label:
                seqs_id[node.node_id][node_label] = seqs_index_count[node_label]
                seqs_index_count[node_label] += 1
        return seqs_id

    @lru_cache
    def prepare_data3(self):
        """准备每一条序列的真实值之间的关系
        {
            seq_id:{
                index: postion
            }
        }
        """
        truth_index = {}
        for label in self.label:
            truth_index[label] = {}
        
        for fake_index, fake in enumerate(self.fake):
            s = 0
            for i in fake:
                s += len(i)
            count = 0
            for postion, value in enumerate(fake):
                for _ in value:
                    truth_index[self.label[fake_index]][count] = postion
                    count += 1
        return truth_index
