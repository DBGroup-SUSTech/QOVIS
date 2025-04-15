import os
import sys
import time
from typing import Dict, List

from align.tree_align_algo import TreeAlignAlgo
from entity.trace import Trace

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


from utils.common_io import write_json_obj, read_json_obj


def compute_transform(trace: Trace):
    trace.costs = costs = []
    trace.transform_lists = transform_lists = []

    start_time = time.time()

    for plan1, plan2 in zip(trace.plans[:-1], trace.plans[1:]):
        align = TreeAlignAlgo(plan1, plan2)

        min_cost = align.get_min_cost()
        align_tree = align.get_align_tree()
        transforms = align_tree.get_transforms()


        # print('min_cost:', min_cost)
        # print('plan1:')
        # print(plan1.to_tree_str())
        # print('plan2:')
        # print(plan2.to_tree_str())
        # print('align_tree:')
        # print(align_tree.to_tree_str())
        # print()

        costs.append(min_cost)
        transform_lists.append(transforms)

    end_time = time.time()
    print('time:', end_time - start_time)
    print('avg time per exec:', (end_time - start_time) / (len(trace.plans) - 1))


def main():
    dataset = 'data6'

    proc_path = os.path.join(ROOT_PATH, 'data', dataset, 'proc')
    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')

    example_list = os.listdir(proc_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    # example_list = list(filter(lambda x: x.startswith('ssb'), example_list))
    # example_list = list(filter(lambda x: x.startswith('bug'), example_list))
    example_list.sort()

    # example_list = ['ssb-q1']
    # example_list = [f"ssb-q{i}" for i in range(1, 14)]

    for example_name in example_list:
        filepath = os.path.join(result_path, example_name, 'trace.json')

        if not os.path.exists(filepath):
            print(example_name, 'trace.json not exists')
            continue

        print(example_name, 'build transform')

        obj = read_json_obj(filepath)
        trace = Trace.load(obj)

        compute_transform(trace)

        # write it back
        # write_json_obj(filepath, trace.dump())

        print()


if __name__ == '__main__':
    main()
