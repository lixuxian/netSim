import networkx as nx


class Routing:
    proxy: str

    def __init__(self, proxy='weight'):
        self.proxy = proxy

    def all_paths(self, graph: nx.Graph):
        """
        :param graph: 拓扑图
        :return: a list of hops from src to dist
        """
        if self.proxy == 'weight':
            return nx.all_pairs_dijkstra_path(graph, weight='weight')
        else:
            return nx.all_pairs_shortest_path(graph)

    def single_path(self, graph: nx.Graph, src, dst, proxy='weight'):
        try:
            if self.proxy == 'weight':
                return nx.shortest_path(graph, source=src, target=dst, weight='weight', method='dijkstra')
            else:
                return nx.shortest_path(graph, src, dst)
        except nx.exception.NetworkXNoPath:
            return None
