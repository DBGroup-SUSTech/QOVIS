import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

if __name__ == '__main__':
    from utils.common_io import read_json_obj, write_lines
    from common.dynamic_graph import DynamicGraph

    dataset = 'data1'

    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')
    stat_path = os.path.join(ROOT_PATH, 'data', dataset, 'stat')

    example_list = os.listdir(result_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()
    example_list = example_list

    lines = []
    for example_name in example_list:
        in_filepath = os.path.join(result_path, example_name, 'dynamic_graph.json')
        dg = DynamicGraph.load(read_json_obj(in_filepath))

        opt_cnt_dict = {}
        for plan in dg.plans:
            for node in plan.node_dict.values():
                cnt = opt_cnt_dict.setdefault(node.name, 0)
                opt_cnt_dict[node.name] = cnt + 1

        for k, v in opt_cnt_dict.items():
            lines.append(f'{example_name},{k},{v}\n')
        print()

    out_filepath = os.path.join(stat_path, 'opt_stat.csv')
    write_lines(out_filepath, lines)


