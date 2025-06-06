import json
from typing import List, Any


def read_lines(filename: str) -> List[str]:
    with open(filename, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    return lines


def read_lines_cond(filename: str, line_filter=(lambda line: True)):
    """ Read all line that satisfies the filter """
    lines = []
    with open(filename, 'r', encoding='utf-8') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            if line_filter(line):
                lines.append(line)
    return lines


def read_json_obj(filename: str):
    with open(filename, 'r', encoding='utf-8') as fp:
        json_obj = json.load(fp)
    return json_obj


def write_lines(filename: str, lines: List[str]):
    with open(filename, 'w', encoding='utf-8') as fp:
        fp.writelines(lines)


def write_json_obj(filename: str, obj: Any, indent=None):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, indent=indent)


def write_csv(filename: str, data: List[List[Any]]):
    with open(filename, 'w', encoding='utf-8') as fp:
        for row in data:
            row = [str(x) for x in row]
            fp.write(','.join(row) + '\n')
