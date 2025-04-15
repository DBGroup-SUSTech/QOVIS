import os
import sys

from utils.common_io import read_json_obj

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


if __name__ == '__main__':
    DATASET = 'data1'
    DATA_PATH = os.path.join(ROOT_PATH, 'data', DATASET)

    example_list = os.listdir(DATA_PATH)

    example_list.sort()

    for example_name in example_list[1:2]:
        summary_path = os.path.join(DATA_PATH, example_name, 'summary')
        for summary_name in os.listdir(summary_path):
            data = read_json_obj(os.path.join(summary_path, summary_name))
            if data['generateStrategy'] == 'ht':
                print(data['k'], data['cost'], data['loss'], data['cost'] + data['loss'], sep='\t')


