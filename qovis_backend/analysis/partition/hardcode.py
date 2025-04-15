from analysis.partition.partition import Partition


class Hardcode(Partition):
    def __init__(self, sg_lst, k):
        super().__init__('hardcode', sg_lst, k)

    def execute(self):
        pass
