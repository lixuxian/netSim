from net_generator import *
import networkx as nx
from tx_generator import Transaction
from routing import Routing
import logging
import matplotlib

matplotlib.rcParams['backend'] = 'SVG'
import matplotlib.pyplot as plt


class Simulator:
    graph: MyGraph
    MST: nx.Graph
    tx: Transaction
    routing: Routing
    shortcuts: []
    paths: Dict[Tuple, List]

    min_balance = 0
    max_balance = 0

    tx_count = 0

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

    def run(self):
        # logging.info(self.MST.edges.data('weight'))
        # self.test()
        for t in self.tx.tx_list:
            self.tx_count += 1
            # get path
            if (t.source, t.destination) not in self.paths:
                path = self.routing.single_path(self.MST, t.source, t.destination, proxy='weight')
            else:
                path = self.paths[(t.source, t.destination)]
            # verify
            logging.info("tx from %d to %d, total %d coin" % (t.source, t.destination, t.money))
            logging.info("path: %s" % str(path))
            if path is None or not self.verify_path(t, path):
                logging.warning("path unavailable, start reroute in whole graph")
                # TODO reroute algorithm
                path = self.routing.single_path(self.graph.nx_graph, t.source, t.destination, proxy='weight')
                if path is None or not self.verify_path(t, path):
                    logging.warning("path unavailable again, transaction failed !!!!!")
                continue
            # backup
            self.paths[(t.source, t.destination)] = path

            # run
            self.change_balance(t, path)
            logging.info("finish %d tx" % self.tx_count)

        # for (pair, channel) in self.graph.channels_obj.items():
        #     print("pair : ", pair, ", balance : ", channel.alice_balance, " <--> ", channel.bob_balance)

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
    sim = Simulator(10, 12, 200, 4000, 2000, 1, 100)
    sim.run()
