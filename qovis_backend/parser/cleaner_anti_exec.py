import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from utils.common_io import read_lines_cond


def filter_log(raw_path: str, example_name: str):
    print('filter_log', example_name)

    in_filepath = os.path.join(raw_path, example_name, 'log.txt')

    return read_lines_cond(in_filepath, lambda x: '[RECORD]' not in x)


def dump_anti_log(raw_path: str, example_name: str, data):
    raw_anti_path = os.path.join(raw_path, example_name, 'log.anti.txt')
    with open(raw_anti_path, 'w') as fp:
        for line in data:
            fp.write(line)


def main():
    dataset = 'data3'

    raw_path = os.path.join(ROOT_PATH, 'data', dataset, 'raw')

    # example_list = os.listdir(raw_path)
    # example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    # example_list.sort()

    example_list = ['bug4-0', 'bug4-2']
    # example_list = ['bug1']

    for example_name in example_list:
        lines = filter_log(raw_path, example_name)
        dump_anti_log(raw_path, example_name, lines)

        print()


if __name__ == '__main__':
    main()


