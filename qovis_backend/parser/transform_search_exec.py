import os
import sys
import time
import argparse

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from entity.trace2 import Trace2
# from trans.algo.min_step_extractor3 import MinStepExtractor3
from trans.algo.trans_path_searcher_ahp import TransPathSearcherAHP
from trans.algo.rule_list import RULE_LIST
from utils.common_io import write_json_obj, read_json_obj
from entity.trace import Trace
from trans.plan.plan_parser import PlanParser
from trans.plan.query_plan import QueryPlan
from trans.rule.trans_path import TransPath
from config.hidden_prints import HiddenPrints
from config.config import TRANS_DEBUG_PRINT


args = argparse.ArgumentParser()
args.add_argument('-d', '--dataset', type=str)
args.add_argument('-t', '--timeout', default=5, type=int)

args = args.parse_args()

ARG_DATASET = args.dataset
ARG_TIMEOUT = args.timeout



def compute_transform(trace: Trace, plans: list[QueryPlan]):
    transforms = []
    costs = []

    start_idx, end_idx = trace.trace_tree.find_step_plan_indices('Optimization')

    start_time = time.time()

    for idx in range(len(plans) - 1):
        p0 = plans[idx]
        p1 = plans[idx + 1]

        # extractor = MinStepExtractor3(p0, p1, NORMAL_RULE_LIST, REORDER_RULE_LIST, normal_timeout=3)
        extractor = TransPathSearcherAHP(p0, p1, RULE_LIST, timeout=ARG_TIMEOUT)
        extractor.precompute()

        # rule_path = extractor.execute()

        # testing
        if start_idx <= idx < end_idx:
            with HiddenPrints(TRANS_DEBUG_PRINT):
                rule_path = extractor.execute()
        else:
            rule_path = None
        # rule_path = None

        start0 = time.time()
        with HiddenPrints(TRANS_DEBUG_PRINT):
            trans = TransPath.mk_transform_path(p0, p1, rule_path)
        trans_time = time.time() - start0
        if trans_time < 0.001:
            trans_time = 0
        # round to ms
        trans_time = round(trans_time * 1000)

        transforms.append(trans)
        costs.append((extractor.get_time_cost(), trans_time))

    end_time = time.time()
    print('time:', end_time - start_time)
    print('avg time per exec:', (end_time - start_time) / (len(plans) - 1))

    return transforms, costs


def main():
    proc_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'proc')
    result_path = os.path.join(ROOT_PATH, 'data', ARG_DATASET, 'result')

    example_list = os.listdir(proc_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()

    for example_name in example_list:
        filepath = os.path.join(result_path, example_name, 'trace.json')
        output_path = os.path.join(result_path, example_name, 'trace2.json')

        if not os.path.exists(filepath):
            print(example_name, 'trace.json not exists')
            continue

        print(example_name, 'solve all plan transform problems')

        obj = read_json_obj(filepath)
        trace = Trace.load(obj)

        parser = PlanParser()
        with HiddenPrints(TRANS_DEBUG_PRINT):
            plans = [parser.parse(p) for p in trace.plans]

        transforms, costs = compute_transform(trace, plans)

        trace2 = Trace2()
        trace2.name = trace.name
        trace2.plans = plans
        trace2.transforms = transforms
        trace2.trace_tree = trace.trace_tree
        trace2.costs = costs

        print(example_name, 'build linkages')
        with HiddenPrints(TRANS_DEBUG_PRINT):
            trace2.build_linkages()

        write_json_obj(output_path, trace2.dump())

        print()


if __name__ == '__main__':
    main()
