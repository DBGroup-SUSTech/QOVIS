import json
import os
import re
import sys
import time

from align.tree_align_algo import TreeAlignAlgo
from align.tree_align_algo_generic import TreeNode, TreeAlignAlgoGeneric
from entity.trace import Trace

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


from utils.common_io import read_json_obj, write_json_obj


def compute_transform(trees: list[TreeNode]):
    transform_lists = []
    for plan1, plan2 in zip(trees[:-1], trees[1:]):
        align = TreeAlignAlgoGeneric(plan1, plan2)

        min_cost = align.get_min_cost()
        align_tree = align.get_align_tree()
        transforms = align_tree.get_transforms()

        transform_lists.append(transforms)
    return transform_lists


def json2tree(obj) -> TreeNode:
    nodes = []
    for v in obj['nodes']:
        s = v['str']
        # remove all #\d+
        s = re.sub(r'#\d+', '', s)
        node = TreeNode(v['vid'], v['name'], s)
        nodes.append(node)
    vid2node = {node.vid: node for node in nodes}
    for v in obj['nodes']:
        node = vid2node[v['vid']]
        node.children = [vid2node[vid] for vid in v['children']]
    return vid2node[obj['root']]


def main():
    dataset = 'data6'

    test_path = os.path.join(ROOT_PATH, 'data', dataset, 'test')

    example_list = os.listdir(test_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    # example_list = list(filter(lambda x: x.startswith('ssb'), example_list))
    # example_list = list(filter(lambda x: x.startswith('bug'), example_list))
    example_list.sort()

    # example_list = ['ssb-q1']
    # example_list = [f"ssb-q{i}" for i in range(1, 14)]

    for example_name in example_list:
        filepath = os.path.join(test_path, example_name)

        with open(filepath, 'r') as f:
            lines = f.readlines()
        datas = [json.loads(line) for line in lines]

        if len(datas) <= 2:
            print(example_name, 'too short')
            continue

        if len(datas[2]) > 4:
            print(example_name, 'already has transforms')
            continue

        # src and dst
        src = json2tree(datas[0][2])
        dst = json2tree(datas[1][2])

        for d in datas[2:]:
            tree = json2tree(d[2])
            transforms = compute_transform([src, tree, dst])
            if len(d) < 5:
                d.append(None)
            d[4] = [[t.dump() for t in lst] for lst in transforms]

        # write it back
        with open(filepath, 'w') as f:
            for d in datas:
                f.write(json.dumps(d) + '\n')

        print()


if __name__ == '__main__':
    main()
