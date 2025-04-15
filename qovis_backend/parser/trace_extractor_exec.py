import os
import sys
from typing import Dict, List
import argparse

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


from trace_extractor import TraceExtractor
from utils.common_io import write_json_obj, read_json_obj


args = argparse.ArgumentParser()
args.add_argument('-d', '--dataset', type=str)

args = args.parse_args()

ARG_DATASET = args.dataset


def load_records(proc_path: str, example_name: str):
    records_filepath = os.path.join(proc_path, example_name, 'records.json')
    return read_json_obj(records_filepath)


def main():
    proc_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'proc')
    result_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'result')

    example_list = os.listdir(proc_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()

    for example_name in example_list:
        result_example_path = os.path.join(result_path, example_name)
        out_filepath = os.path.join(result_path, example_name, 'trace.json')

        if not os.path.exists(result_example_path):
            os.makedirs(result_example_path)

        if os.path.exists(out_filepath):
            print(example_name, 'trace already exists')
            continue

        print(example_name, 'build trace')

        records = load_records(proc_path, example_name)
        extractor = TraceExtractor(records)
        extractor.exec()
        trace = extractor.get()

        write_json_obj(out_filepath, trace.dump())

        print()


if __name__ == '__main__':
    main()
