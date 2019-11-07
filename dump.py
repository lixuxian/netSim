from net_generator import *
from tx_generator import *
import time
import os


class Dump:

    def __init__(self, root_dir='./dumpfile/'):
        self.root_dir = root_dir
        time_str = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        self.project_dir = self.root_dir + time_str + '/'
        if not os.path.exists(self.project_dir):
            os.mkdir(self.project_dir)
        self.tx_filepath = self.project_dir + 'tx.csv'
        self.node_filepath = self.project_dir + 'node.csv'
        self.channel_filepath = self.project_dir + 'channel.csv'

    def dump_files(self, graph: MyGraph, tx: Transaction):
        self.dump_nodes(graph)
        self.dump_channels(graph)
        self.dump_transactions(tx)

    def dump_nodes(self, graph: MyGraph):
        f = open(self.node_filepath, 'x')
        f.write('node_id,amount\n')
        for n in graph.nodes_obj:
            line = str(n.node_id) + ',' + str(sum(n.balances)) + '\n'
            f.write(line)
        f.close()

    def dump_channels(self, graph: MyGraph):
        f = open(self.channel_filepath, 'x')
        f.write('alice,bob,alice_balance,bob_balance\n')
        for (pair, channel) in graph.channels_obj.items():
            line = str(channel.alice) + ',' + str(channel.bob) + ',' + str(channel.alice_balance) \
                   + ',' + str(channel.bob_balance) + '\n'
            f.write(line)
        f.close()

    def dump_transactions(self, tx: Transaction):
        f = open(self.tx_filepath, 'x')
        f.write('source,destination,money\n')
        for t in tx.tx_list:
            line = str(t.source) + ',' + str(t.destination) + ',' + str(t.money) + '\n'
            f.write(line)
        f.close()
