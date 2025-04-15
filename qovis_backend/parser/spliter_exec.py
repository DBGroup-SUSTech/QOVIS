import json
import os
import sys
from typing import List, Dict
import argparse

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from utils.common_io import write_lines, read_lines, write_json_obj


args = argparse.ArgumentParser()
args.add_argument('-d', '--dataset', type=str)

args = args.parse_args()

ARG_DATASET = args.dataset


def split_log(raw_path: str, example_name: str) -> (List[str], List[Dict], List[int]):
    """
    Split log into two parts: cleaned logs and cleaned records.
    We map each record to its corresponding position in the cleaned log.
    E.g., log_map[0] = 0 means the first record should occur before the first line of the cleaned log.
    """
    print('split_log', example_name)

    in_filepath = os.path.join(raw_path, example_name, 'log.txt')
    lines = read_lines(in_filepath)

    log_lines = []
    record_lines = []
    log_map = []
    meet_start_flag = False

    for line in lines:
        if not meet_start_flag:
            if '[RECORD] [START]' in line:
                meet_start_flag = True
                # don't process this line
            elif '[RECORD]' not in line:
                log_lines.append(line)
        else:
            if '[RECORD]' in line:
                record_lines.append(line)
                log_map.append(len(log_lines))
            else:
                log_lines.append(line)

    assert meet_start_flag

    records = []
    for line in record_lines:
        json_str = line.split('[RECORD]')[1]
        record = json.loads(json_str)
        records.append(record)

    return log_lines, records, log_map


def main():
    raw_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'raw')
    proc_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'proc')

    example_list = os.listdir(raw_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()

    # example_list = ['bug0-0', 'bug0-1', 'bug1-0', 'bug4-0']
    # example_list = ['bug1']

    for example_name in example_list:
        proc_example_path = os.path.join(proc_path, example_name)
        cleaned_logs_filepath = os.path.join(proc_path, example_name, 'log.clean.txt')
        cleaned_records_filepath = os.path.join(proc_path, example_name, 'records.json')
        map_filepath = os.path.join(proc_path, example_name, 'map.txt')

        if not os.path.exists(proc_example_path):
            os.makedirs(proc_example_path)
        else:
            # skip this example if both files exist
            if os.path.exists(cleaned_logs_filepath) and os.path.exists(cleaned_records_filepath):
                print('skip', example_name)
                continue

        cleaned_logs, cleaned_records, log_map = split_log(raw_path, example_name)
        write_lines(cleaned_logs_filepath, cleaned_logs)
        write_json_obj(cleaned_records_filepath, cleaned_records)
        write_lines(map_filepath, [' '.join(map(str, log_map))])

        print()


if __name__ == '__main__':
    main()


