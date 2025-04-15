import os
import sys
FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

import json
from common.trace_graph import TGraph
from utils.common_io import read_lines_cond, write_lines, read_json_obj


def extract_trace_data(example_path: str):
    example_name = os.path.split(example_path)[1]
    print('extract_trace_data', example_name)

    in_filepath = os.path.join(example_path, 'log.txt')
    out_filepath = os.path.join(example_path, 'raw_trace.json')

    lines = read_lines_cond(in_filepath, lambda x: '[RECORD]' in x)
    records = []
    for line in lines:
        json_str = line.split('[RECORD]')[1]
        data = json.loads(json_str)
        if data['effective']:
            records.append(data)
    result_str = json.dumps(records)

    write_lines(out_filepath, [result_str])

    effective = len(records)
    total = len(lines)
    print(f'{example_name}: {effective} / {total} = {effective / total * 100: .2f}%')


def build_trace_dag(example_path: str):
    example_name = os.path.split(example_path)[1]
    print('build_trace_dag', example_name)

    in_filepath = os.path.join(example_path, 'raw_trace.json')
    out_filepath = os.path.join(example_path, 'trace_dag.json')

    records = read_json_obj(in_filepath)
    tg = TGraph()
    tg.build_from_raw_trace(records)

    result_str = json.dumps(tg.to_dict())
    write_lines(out_filepath, [result_str])


def cp_data(data_path: str, output_path: str, example_name: str):
    print('cp_data', example_name)

    in_example_path = os.path.join(data_path, example_name)
    out_example_path = os.path.join(output_path, example_name)
    if not os.path.exists(out_example_path):
        os.makedirs(out_example_path)

    filenames = ['trace_dag.json']

    for filename in filenames:
        in_filepath = os.path.join(in_example_path, filename)
        out_filepath = os.path.join(out_example_path, filename)
        data = read_lines_cond(in_filepath)
        write_lines(out_filepath, data)


if __name__ == '__main__':
    DATASET = 'data1'
    DATA_PATH = os.path.join(ROOT_PATH, 'data', DATASET)
    OUTPUT_PATH = os.path.join(ROOT_PATH, os.pardir, 'qotrace-frontend', 'src/assets/data', DATASET)

    example_list = os.listdir(DATA_PATH)
    # example_list = ['bug0']

    example_list.sort()

    for example_name in example_list:
        example_path = os.path.join(DATA_PATH, example_name)
        extract_trace_data(example_path)
        build_trace_dag(example_path)
        print()


