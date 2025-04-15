import os
from enum import Enum

from common.dynamic_graph import DynamicGraph
from utils.common_io import read_json_obj, write_json_obj


class ExtractStrategy(Enum):
    RAND = 'r'
    KEEP_ALL = 'ka'
    STAGE = 's'


class GenerateStrategy(Enum):
    MERGE_ALL = 'ma'
    NOOP = 'n'
    STRUCT = 's'
    TIMELINE = 'tl'
    TIMELINE_COST = 'tlc'


class SummaryAlgo:
    def __init__(self, example_path, extract_strategy, generate_strategy):
        self.example_name = os.path.split(example_path)[1]
        self.example_path = example_path

        # algo type
        self.extract_strategy: ExtractStrategy = extract_strategy
        self.generate_strategy: GenerateStrategy = generate_strategy

        # input
        self.dg: DynamicGraph = None
        self.k = None

        # output
        self.summary = None
        self.cost = None
        self.loss = None

    def execute(self):
        print('compute summarization', self.example_name)

        in_filepath = os.path.join(self.example_path, 'dynamic_graph.json')

        self.dg = DynamicGraph.load(read_json_obj(in_filepath))
        self.k = 7

        self._execute_algo()

        summary_path = os.path.join(self.example_path, 'summary')
        if not os.path.exists(summary_path):
            os.mkdir(summary_path)

        out_filename = f'summary' \
                       f'_{self.k}' \
                       f'_{self.extract_strategy.value}' \
                       f'_{self.generate_strategy.value}' \
                       f'.json'
        out_filepath = os.path.join(summary_path, out_filename)
        result = {
            'example': self.example_name,
            'extractStrategy': self.extract_strategy.value,
            'generateStrategy': self.generate_strategy.value,

            'k': self.k,

            'summary': self.summary,
            'cost': self.cost,
            'loss': self.loss,
        }
        write_json_obj(out_filepath, result, indent=2)

    def _execute_algo(self):
        return None
