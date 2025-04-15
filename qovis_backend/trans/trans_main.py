import os
import sys
import time

from test.trans.common import init_file
from trans.algo.min_delta_extractor import MinDeltaExtractor
from trans.algo.min_step_extractor import MinStepExtractor
from trans.algo.min_step_extractor2 import MinStepExtractor2

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


from entity.trace import Trace
from trans.plan.plan_parser import PlanParser
from utils.common_io import read_json_obj
from trans.algo.trans_extractor import TransExtractor
from trans.algo.rule_list import RULE_LIST


def compute_transform(trace: Trace):
    trace.costs = costs = []
    trace.transform_lists = transform_lists = []

    plan_parser = PlanParser()
    plans = trace.plans
    # plans = plans[7:9]        # bug0-0 CollapseProject
    # plans = plans[6:8]      # bug0-0 ColumnPruning
    # plans = plans[5:7]      # ssb-q1 - PushDownPredicates
    # plans = plans[6:8]      # ssb-q1 - ColumnPruning
    # plans = plans[5:8]      # ssb-q1 - Optimization phase
    # plans = plans[6:8]      # ssb-q10 - PushDownPredicates
    plans = plans[5:7]      # ssb-q11 - JoinReorder
    plans = [plan_parser.parse(p) for p in plans]

    start_time = time.time()

    for plan1, plan2 in zip(plans[:-1], plans[1:]):
        # extractor = TransExtractor(plan1, plan2, RULE_LIST)
        # extractor = MinStepExtractor(plan1, plan2, RULE_LIST)

        # log_filepath = os.path.join(ROOT_PATH, 'data/data6/test/ssb-q1-op-phase.jsonl')
        # log_filepath = os.path.join(ROOT_PATH, 'data/data6/test/ssb-q10-pd.jsonl')
        log_filepath = os.path.join(ROOT_PATH, 'data/data6/test/ssb-q11-join-reorder.jsonl')
        # log_filepath = os.path.join(ROOT_PATH, 'data/data6/test/ssb-q1-op-phase-delta.jsonl')
        # log_filepath = os.path.join(ROOT_PATH, 'data/data6/test/ssb-q10-pd-delta.jsonl')
        init_file(log_filepath)
        extractor = MinStepExtractor2(plan1, plan2, RULE_LIST, log_filepath, sample_rate=0)
        # extractor = MinDeltaExtractor(plan1, plan2, RULE_LIST, log_filepath, sample_rate=0)

        extractor.precompute()

        exec_start_time = time.time()

        rule_path = extractor.execute()

        exec_end_time = time.time()

        # print('min_cost:', min_cost)
        # print('plan1:')
        # print(plan1.to_tree_str())
        # print('plan2:')
        # print(plan2.to_tree_str())
        # print('align_tree:')
        # print(align_tree.to_tree_str())
        # print()

        # transform_lists.append(transforms)

        if rule_path is None:
            print(plan1, plan2, 'no path found')
        else:
            print(plan1, plan2, [r.name for r in rule_path])
        print('attempt_count:', extractor.attempt_count)
        print('generated_plan_count:', extractor.generated_plan_count)
        print('exec_time:', exec_end_time - exec_start_time)

    end_time = time.time()
    print('time:', end_time - start_time)
    print('plan pair #:', len(plans) - 1)
    print('avg time per exec:', (end_time - start_time) / (len(plans) - 1))


def main():
    dataset = 'data6'

    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')

    trace_list = os.listdir(result_path)
    trace_list = list(filter(lambda x: not x.startswith('.'), trace_list))
    # trace_list = list(filter(lambda x: x.startswith('ssb'), example_list))
    # trace_list = list(filter(lambda x: x.startswith('bug'), example_list))
    trace_list.sort()

    # trace_list = ['bug0-0']
    # trace_list = ['ssb-q1']
    # trace_list = ['ssb-q10']
    trace_list = ['ssb-q11']
    # trace_list = [f"ssb-q{i}" for i in range(1, 14)]

    for example_name in trace_list:
        trace_filepath = os.path.join(result_path, example_name, 'trace.json')

        print(example_name, 'build trace')

        obj = read_json_obj(trace_filepath)
        trace = Trace.load(obj)

        compute_transform(trace)

        # write_json_obj(trace_filepath, trace.dump())

        print()


if __name__ == '__main__':
    main()
