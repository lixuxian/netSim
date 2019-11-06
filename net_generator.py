import networkx as nx
import random
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import logging

k1 = 0.5
k2 = 0.5


class Node:

    def __init__(self, node_id):
        self.node_id = node_id
        self.amount_balance = 0
        self.neighbor_num = 0
        self.neighbors: List = []
        self.balances: List = []


class Channel:

    def __init__(self, alice, bob, alice_balance, bob_balance):
        assert 0 <= alice != bob >= 0
        assert alice_balance >= 0 and bob_balance >= 0
        self.alice = alice
        self.bob = bob
        self.alice_balance = alice_balance
        self.bob_balance = bob_balance
        self.balance_dict = Dict[int, int]
        self.amount_balance = self.alice_balance + self.bob_balance
        self.weight = 0
        self.alice_node_obj: Node = None
        self.bob_node_obj: Node = None

    def calculate_weight(self):
        self.weight = k1 * (1 - self.amount_weight()) + k2 * self.balance_weight()
        # logging.info(self.alice, " --> ", self.bob, "weight = ", self.weight)
        logging.info("%d --> %d, weight = %f" % (self.alice, self.bob, self.weight))

    def balance_weight(self):
        return abs(self.alice_balance - self.bob_balance) / self.amount_balance

    def amount_weight(self):
        return self.amount_balance / self.alice_node_obj.amount_balance


class MyGraph:

    def __init__(self, nodes, edges, minb, maxb):
        assert nodes > 0 and edges > 0
        self.node_num = nodes
        self.edge_num = edges
        self.min_balance = minb
        self.max_balance = maxb
        # self.nx_graph = nx.erdos_renyi_graph(self.node_num, 0.3)
        # self.nx_graph = nx.watts_strogatz_graph(self.node_num, 3, 0.5)
        self.nx_graph = nx.gnm_random_graph(self.node_num, self.edge_num)
        self.nodes_obj: List[Node] = []  # list of class Node
        # self.channels_obj: List[Channel] = []  # list of class Channel
        self.channels_obj: Dict[Tuple, Channel] = {}

        self.generate_nodes()
        self.generate_channels()
        self.calculate_weights()

        # self.draw_graph()

    def generate_nodes(self):
        # generate node_num nodes
        logging.info("generate nodes")
        for i in range(self.node_num):
            self.nodes_obj.append(Node(i))

    def generate_channels(self):
        logging.info("generate channels")
        for edge in self.nx_graph.edges:
            # channel : edge[0] <--> edge[1]

            alice = edge[0]
            bob = edge[1]
            alice_balance = random.randint(self.min_balance, self.max_balance)
            bob_balance = random.randint(self.min_balance, self.max_balance)
            logging.info("%d --> %d : %d vs %d" % (alice, bob, alice_balance, bob_balance))

            self.nodes_obj[alice].amount_balance += alice_balance + bob_balance
            self.nodes_obj[alice].neighbor_num += 1
            self.nodes_obj[alice].neighbors.append(bob)
            self.nodes_obj[alice].balances.append(alice_balance)

            self.nodes_obj[bob].amount_balance += alice_balance + bob_balance
            self.nodes_obj[bob].neighbor_num += 1
            self.nodes_obj[bob].neighbors.append(alice)
            self.nodes_obj[bob].balances.append(bob_balance)

            channel = Channel(alice, bob, alice_balance, bob_balance)
            channel.alice_node_obj = self.nodes_obj[alice]
            channel.bob_node_obj = self.nodes_obj[bob]
            # self.channels_obj.append(channel)
            self.channels_obj[(alice, bob)] = channel

    def calculate_weights(self):
        logging.info("calculate weights")
        for (pair, channel) in self.channels_obj.items():
            channel.calculate_weight()
            self.nx_graph[channel.alice][channel.bob]['weight'] = channel.weight

    def draw_graph(self):
        plt.subplot(111)
        nx.draw(self.nx_graph, pos=nx.spring_layout(self.nx_graph, iterations=20), node_size=80, with_labels=True)
        plt.show()


# if __name__ == '__main__':
#     simulate()
