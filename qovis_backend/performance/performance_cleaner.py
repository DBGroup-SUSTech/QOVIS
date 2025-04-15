import os
import sys
import csv
import argparse

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

arg_parser = argparse.ArgumentParser(description='Clean the performance data')
arg_parser.add_argument('-d', '--data', required=True, type=str, help='Input data file name')
arg_parser.add_argument('-o', '--output', required=True, type=str, help='Output file name')
# arg_parser.add_argument('--part_include', action='store_true', help='Include the partial data')

args = arg_parser.parse_args()
arg_data = args.data
arg_output = args.output
# part_include = args.part_include

# print args
print('Data:', arg_data)
print('Output:', arg_output)
# print('Include partial data:', part_include)


def main():
    # read data as csv
    with open(arg_data, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = list(reader)

    # clean data
    # only keep the last row of each (case, step name, method) test_case_id (id: 1, 2, 3)
    cleaned_data = []
    test_case_id_set = set()
    for row in data[::-1]:
        test_case_id = (row[1], row[2], row[3])
        if test_case_id not in test_case_id_set:
            cleaned_data.append(row)
            test_case_id_set.add(test_case_id)

    # reverse the cleaned data
    cleaned_data = cleaned_data[::-1]

    # remove partial data
    # only keep the all three record (case, step name) for 3 methods
    # and not all of them has a path length = -1
    cleaned_data2 = []
    category_id_to_data = {}
    for row in cleaned_data:
        category_id = (row[1], row[2])
        if category_id not in category_id_to_data:
            category_id_to_data[category_id] = []
        category_id_to_data[category_id].append(row)
    for category_id in category_id_to_data:
        if len(category_id_to_data[category_id]) == 3 \
                and not all(row[6] == '-1' for row in category_id_to_data[category_id]):
            cleaned_data2.extend(category_id_to_data[category_id])
            # insert correct path length: remove -1, all other path length should be the same
            path_length = None
            for row in category_id_to_data[category_id]:
                if row[6] != '-1':
                    path_length = row[6]
                    break
            for row in category_id_to_data[category_id]:
                row[6] = path_length

    cleaned_data = cleaned_data2


    # write cleaned data to output file
    with open(arg_output, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(cleaned_data)


if __name__ == '__main__':
    main()
