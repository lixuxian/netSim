class Statistics:
    tx_count = 0  # tx_count = tx_success + tx_fail
    tx_success = 0
    tx_fail = 0

    routing_count = 0
    no_routing_count = 0
    one_time_routing_count = 0

    re_routing_count = 0  # re_routing_count = re_routing_success + re_routing_fail
    re_routing_success = 0
    re_routing_fail = 0

    def tx_success_ratio(self):
        return self.tx_success / self.tx_count

    def tx_fail_ratio(self):
        return self.tx_fail / self.tx_count

    def avg_routing_time(self):
        return self.routing_count / self.tx_count

    def show_stats(self):
        print("tx_count = %d, tx_success = %d, tx_fail = %d, tx_success_ratio = %f"
              % (self.tx_count, self.tx_success, self.tx_fail, self.tx_success_ratio()))
        print("routing_count = %d, no_routing_count = %d, one_time_routing_count = %d, "
              "re_routing_count = %d, re_routing_success = %d, re_routing_fail = %d"
              % (self.routing_count, self.no_routing_count, self.one_time_routing_count,
                 self.re_routing_count, self.re_routing_success, self.re_routing_fail))
        print("avg_routing_time = %f" % self.avg_routing_time())
