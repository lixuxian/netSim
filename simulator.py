from net_generator import *
import networkx as nx
from tx_generator import Transaction
from routing import Routing
import logging
import matplotlib.pyplot as plt
from statistics import Statistics
from dump import *


class Simulator:
    graph: MyGraph
    MST: nx.Graph
    tx: Transaction
    routing: Routing
    shortcuts: []
    paths: Dict[Tuple, List]

    min_balance = 0
    max_balance = 0

    stats: Statistics

    dumper: Dump

    def __init__(self, nodes, edges, minb, maxb, tx_num, tx_min, tx_max):
        assert nodes > 0 and edges > 0
        assert 0 <= minb <= maxb
        assert 0 < tx_min <= tx_max
        self.min_balance = minb
        self.max_balance = maxb
        self.graph = MyGraph(nodes, edges, minb, maxb)
        self.MST = nx.minimum_spanning_tree(self.graph.nx_graph, weight='weight', algorithm='prim')
        self.tx = Transaction(nodes, tx_num, tx_min, tx_max)
        self.routing = Routing(proxy='weight')
        self.paths = {}
        self.stats = Statistics()
        self.dumper = Dump()
        self.dumper.dump_files(self.graph, self.tx)

    def setup(self):
        pass

    def shortcuts(self):
        pass

    def verify_path(self, t: Transaction.Tx, path: List) -> bool:
        for i in range(len(path) - 1):
            if (path[i], path[i + 1]) in self.graph.channels_obj:
                ch = self.graph.channels_obj[(path[i], path[i + 1])]
            else:
                ch = self.graph.channels_obj[(path[i + 1], path[i])]
            if (ch.alice == path[i] and ch.alice_balance < t.money) or \
                    (ch.bob == path[i] and ch.bob_balance < t.money):
                logging.warning("ch.alice_balance < t.money")
                logging.warning("stop a unavailable tx")
                return False
        return True

    def change_balance(self, t: Transaction.Tx, path: List):
        # change balance
        for i in range(len(path) - 1):
            if (path[i], path[i + 1]) in self.graph.channels_obj:
                ch = self.graph.channels_obj[(path[i], path[i + 1])]
            else:
                ch = self.graph.channels_obj[(path[i + 1], path[i])]
            if ch.alice == path[i]:
                ch.alice_balance -= t.money
                ch.bob_balance += t.money
            else:
                ch.alice_balance += t.money
                ch.bob_balance -= t.money

    def refresh_weight(self):
        for (pair, channel) in self.graph.channels_obj.items():
            channel.calculate_weight()

    def execute_transaction(self, t: Transaction.Tx, path) -> bool:
        if path is None or path is []:
            return False
        if not self.verify_path(t, path):
            return False
        self.change_balance(t, path)
        return True

    def route(self, t: Transaction.Tx) -> bool:
        path = self.routing.single_path(self.MST, t.source, t.destination, proxy='weight')
        self.stats.routing_count += 1
        self.paths[(t.source, t.destination)] = path
        if self.execute_transaction(t, path):
            self.stats.tx_success += 1
            self.stats.one_time_routing_count += 1
            return True
        else:
            return False

    def reroute(self, t: Transaction.Tx) -> bool:
        path = self.routing.single_path(self.graph.nx_graph, t.source, t.destination, proxy='weight')
        self.stats.re_routing_count += 1
        if self.execute_transaction(t, path):
            self.stats.tx_success += 1
            self.stats.re_routing_success += 1
            logging.info("reroute success")
            return True
        else:
            self.stats.tx_fail += 1
            self.stats.re_routing_fail += 1
            logging.warning("reroute failed!!!")
            return False

    def run(self):
        # self.dumper.dump_files(self.graph, self.tx)
        # logging.info(self.MST.edges.data('weight'))
        # self.test()
        for t in self.tx.tx_list:
            self.stats.tx_count += 1
            if (t.source, t.destination) in self.paths:   # if exist available path
                path = self.paths[(t.source, t.destination)]
                if self.execute_transaction(t, path):  # valid path, no routing
                    self.stats.no_routing_count += 1
                    self.stats.tx_success += 1
                else:  # not valid path, reroute
                    if not self.route(t):
                        self.reroute(t)
            else:  # don't exist path now
                if not self.route(t):
                    self.reroute(t)
            logging.info("finish %d tx" % self.stats.tx_count)
        self.stats.show_stats()

    def test(self):
        print(self.routing.single_path(self.MST, 1, 2))
        print(self.routing.single_path(self.MST, 1, 6))
        print(self.routing.single_path(self.MST, 1, 8))
        self.draw_graph(save=True)

    def draw_graph(self, save=False):
        plt.figure(figsize=[16.4, 14.8])
        plt.subplot(121)
        edge_labels_g = dict([((u, v,), round(d['weight'], 2)) for u, v, d in self.graph.nx_graph.edges(data=True)])
        pos_g = nx.spring_layout(self.graph.nx_graph)
        nx.draw(self.graph.nx_graph, pos=pos_g, node_size=160, with_labels=True)
        nx.draw_networkx_edge_labels(self.graph.nx_graph, pos=pos_g, edge_labels=edge_labels_g, font_size=16, alpha=0.5)

        plt.subplot(122)
        pos_mst = nx.spring_layout(self.MST)
        edge_labels_mst = dict([((u, v,), round(d['weight'], 2)) for u, v, d in self.MST.edges(data=True)])
        nx.draw(self.MST, pos=pos_mst, node_size=160, with_labels=True, edge_color='r', node_color='#ffaa00')
        nx.draw_networkx_edge_labels(self.MST, pos=pos_mst, edge_labels=edge_labels_mst, font_size=16, alpha=0.5)
        if save:
            pic_name = 'graph_' + str(self.graph.node_num) + '_' + str(self.graph.edge_num) + '.svg'
            plt.savefig('./pic/' + pic_name, format='svg')
        plt.show()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sim = Simulator(5, 7, 200, 4000, 2000, 1, 100)
    sim.run()
