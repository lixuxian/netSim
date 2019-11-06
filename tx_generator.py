from typing import List
import random
import logging


class Transaction:

    class Tx:
        def __init__(self, src, dst, mny):
            self.source = src
            self.destination = dst
            self.money = mny

    tx_list: List[Tx]

    def __init__(self, node_num, tx_num, min_money, max_money):
        self.tx_num = tx_num
        self.min_money = min_money
        self.max_money = max_money
        self.node_num = node_num
        self.tx_list = []
        self.generate_tx()

    def generate_tx(self):
        logging.info("generate tx...")
        for i in range(self.tx_num):
            src = random.randint(0, self.node_num - 1)
            dst = random.randint(0, self.node_num - 1)
            while dst == src:
                dst = random.randint(0, self.node_num - 1)
            money = random.randint(self.min_money, self.max_money)
            self.tx_list.append(self.Tx(src, dst, money))
        logging.info("generate %d transactions" % len(self.tx_list))
