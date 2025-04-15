import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

import json
from utils.common_io import read_lines_cond, read_lines


def test(raw_path: str, example_name: str):
    print('extract_trace_data', example_name)

    in_filepath = os.path.join(raw_path, example_name, 'log.txt')

    rule_cnt = 0
    apply_cnt = 0

    lines = read_lines(in_filepath)
    for line in lines:
        if '[RECORD]' in line:
            json_str = line.split('[RECORD]')[1]
            data = json.loads(json_str)
            if 'effective' not in data or data['effective'] is True:
                if data['rType'] == 'rule':
                    rule_cnt += 1
        elif line.startswith('=== Applying Rule '):
            apply_cnt += 1
    print(rule_cnt, apply_cnt)


def extract_trace_data(raw_path: str, example_name: str):
    print('extract_trace_data', example_name)

    in_filepath = os.path.join(raw_path, example_name, 'log.txt')

    lines = read_lines_cond(in_filepath, lambda x: '[RECORD]' in x)
    while len(lines) > 0:
        if lines[0].startswith("[RECORD] [START]"):
            lines.pop(0)
            break
        else:
            lines.pop(0)

    records = []
    for line in lines:
        json_str = line.split('[RECORD]')[1]
        data = json.loads(json_str)
        if 'effective' not in data or data['effective'] is True:
            records.append(data)

    effective = len(records)
    total = len(lines)
    print(f'{example_name}: {effective} / {total} = {effective / total * 100: .2f}%')

    return records


def dump_clean_log(clean_path: str, example_name: str, data):
    clean_example_path = os.path.join(clean_path, example_name, 'clean_log.json')
    with open(clean_example_path, 'w') as fp:
        json.dump(data, fp)


if __name__ == '__main__':
    dataset = 'data3'

    raw_path = os.path.join(ROOT_PATH, 'data', dataset, 'raw')
    clean_path = os.path.join(ROOT_PATH, 'data', dataset, 'clean')

    example_list = os.listdir(raw_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()

    for example_name in example_list:
        clean_example_path = os.path.join(clean_path, example_name)

        if not os.path.exists(clean_example_path):
            os.makedirs(clean_example_path)

        # test(raw_path, example_name)

        records = extract_trace_data(raw_path, example_name)
        dump_clean_log(clean_path, example_name, records)

        print()


