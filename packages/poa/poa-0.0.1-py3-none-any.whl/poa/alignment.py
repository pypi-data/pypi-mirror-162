import numpy as np


class AlignmentBase:

    def __init__(self, graph, seq):
        self.graph = graph
        self.seq = seq
        self.l1 = len(graph)
        self.l2 = len(seq)

    def prev_nodes_idx(self, node):
        """ 当前节点的prev节点所属的index """
        return [
            self.graph.node_id2node_index[node_id]
            for node_id in node.in_edge
        ]

    def prev_nodes(self, node):
        """ 当前节点的prev节点 """
        return [
            self.graph.node_id2node[node_id]
            for node_id in node.in_edge
        ]

    def next_nodes(self, node):
        """ 当前节点的next节点 """
        return [
            self.graph.node_id2node[node_id]
            for node_id in node.out_edge
        ]

    def make_score(self, node1, node2):
        raise NotImplementedError()

    def init_align_matrix(self):
        """ 初始化矩阵

            需求：
                - 打分矩阵
                - 回溯结果
                - 融合使用的矩阵
        """
        l1, l2 = self.l1+1, self.l2+1

        # 打分矩阵
        scores = np.zeros((l1, l2), dtype=np.int)

        # 图节点当前位置的最优值来源
        graph_from = np.zeros((l1, l2), dtype=np.int)

        # 序列当前位置的最优值来源
        seq_from = np.zeros((l1, l2), dtype=np.int)

        # 当前位置的节点融合类型
        align_type = np.ones((l1, l2), dtype=np.int)
        return scores, graph_from, seq_from, align_type

    def init_align(self):
        scores, graph_from, seq_from, align_type = self.init_align_matrix()
        return scores, graph_from, seq_from, align_type

    def align(self):
        raise NotImplementedError()

    def traceback(self, scores, graph_from, seq_from, align_type):
        """ 回溯
            生成的结果需要完成两个需求
                - 需要记录序列中哪些的值可以融合到图的节点中
                - 需要记录序列中哪些值需要创建新节点
        """
        # 找到结尾的几个节点
        tail_nodes = [index for (index, node) in enumerate(
            self.graph) if node.out_degree == 0]
        besti, bestj = scores.shape
        besti -= 1
        bestj -= 1
        besti = tail_nodes[0] + 1
        bestscore = scores[besti, bestj]
        for i in tail_nodes[1:]:
            score = scores[i+1, bestj]
            if score > bestscore:
                bestscore, besti = score, i+1
        matches = {}
        while (besti != 0 or bestj != 0):
            nexti, nextj = graph_from[besti, bestj], seq_from[besti, bestj]
            if align_type[besti, bestj] == 0:
                matches[bestj-1] = besti-1
            besti, bestj = nexti, nextj
        return matches


class AlignmentSeq(AlignmentBase):
    """ 多序列比对 """

    def __init__(
        self,
        graph,
        seq,
        match=2,
        mismatch=-4,
        gap=-2,
    ):
        super().__init__(graph, seq)
        self.match = match
        self.mismatch = mismatch
        self.gap = gap

    def make_score(self, s1, s2):
        """ 碱基的打分函数 """
        if s1 == s2:
            return self.match
        return self.mismatch

    def init_align(self):
        scores, graph_from, seq_from, align_type = self.init_align_matrix()
        # 对打分矩阵进行初始化
        gap = self.gap
        # 对第一行进行初始化
        scores[0, :] = np.array([0 + i*gap for i in range(self.l2+1)])

        # 对第一列进行初始化
        for index, node in enumerate(self.graph):
            prev_nodes_idx = self.prev_nodes_idx(node)
            # 当前节点没有prev节点
            if not prev_nodes_idx:
                scores[index+1, 0] = scores[0, 0] + gap
                continue
            # 当前节点有来自多个方向的节点
            best = scores[prev_nodes_idx[0]+1, 0]
            for prev_idx in prev_nodes_idx[1:]:
                best = max(best, scores[prev_idx+1, 0])
            scores[index+1, 0] = best + gap

        return scores, graph_from, seq_from, align_type

    def align(self):
        """ 开始比对
            比对过程中需要记录当前结果来自于那个方向
        """
        scores, graph_from, seq_from, align_type = self.init_align()
        for i, node in enumerate(self.graph):
            prev_nodes_idx = self.prev_nodes_idx(node)
            if not prev_nodes_idx:
                prev_nodes_idx = [-1]
            for j, s in enumerate(self.seq):
                subscores = [
                    (scores[i+1, j] + self.gap, i+1, j, 1)
                ]
                best_score = max([self.make_score(node_str, s)
                                  for node_str in node.value])
                # 计算多个prev节点
                for prev_idx in prev_nodes_idx:
                    subscores.append(
                        (
                            scores[prev_idx+1, j] + best_score,
                            prev_idx+1,
                            j,
                            0,
                        )
                    )
                    subscores.append(
                        (
                            scores[prev_idx+1, j+1] + self.gap,
                            prev_idx+1,
                            j+1,
                            1,
                        )
                    )
                scores[i+1, j+1], graph_from[i+1, j+1], seq_from[i +
                                                                 1, j+1], align_type[i+1, j+1] = max(subscores)

        return self.traceback(scores, graph_from, seq_from, align_type)
