import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

if __name__ == '__main__':
    from parser.dg_converter import DgConverter
    from utils.common_io import write_json_obj, read_json_obj

    def load_clean_log(clean_path: str, example_name: str):
        clean_log_path = os.path.join(clean_path, example_name, 'clean_log.json')
        return read_json_obj(clean_log_path)

    def build_dynamic_graph(result_path: str, example_name: str, records):
        print('build_dynamic_graph', example_name)

        out_filepath = os.path.join(result_path, example_name, 'dynamic_graph.json')

        converter = DgConverter(records)
        converter.exec()
        dg = converter.get()

        write_json_obj(out_filepath, dg.dump())

    dataset = 'data1'

    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')

    example_list = os.listdir(clean_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()
    example_list = example_list[1:2]

    for example_name in example_list:
        result_example_path = os.path.join(result_path, example_name)
        if not os.path.exists(result_example_path):
            os.makedirs(result_example_path)

        records = load_clean_log(clean_path, example_name)
        build_dynamic_graph(result_path, example_name, records)
        print()


