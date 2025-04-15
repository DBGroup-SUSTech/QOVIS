import argparse
import os
import re
import sys
import traceback
from enum import Enum
from datetime import datetime

from trans.algo.algo_status import AlgoStatus

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

from entity.trace import Trace
from trans.plan.plan_parser import PlanParser
from utils.common_io import read_json_obj
from trans.algo.rule_list import NORMAL_RULE_LIST, REORDER_RULE_LIST, RULE_LIST
from trans.plan.query_plan import QueryPlan
from trans.algo.trans_path_searcher_bfs import TransPathSearcherBFS
from trans.algo.trans_path_searcher_ah import TransPathSearcherAH
from trans.algo.trans_path_searcher_ahp import TransPathSearcherAHP


arg_parser = argparse.ArgumentParser(description='Profile the performance of transformation path search algorithm')
arg_parser.add_argument('-o', '--output', type=str, help='Output file name')
arg_parser.add_argument('-c', '--case', type=str, default='.*', help='Only run the case')
arg_parser.add_argument('-m', '--method', type=str, default='.*', help='Only run the method')
arg_parser.add_argument('-t', '--timeout', type=int, default=3, help='Timeout for each test case (in seconds)')
group = arg_parser.add_mutually_exclusive_group(required=False)
group.add_argument('-s', '--step', type=str, help='Only run the step having the step name')
group.add_argument('-i', '--index', type=int, help='Only run the plan pair [plans[index], plans[index+1]]')

args = arg_parser.parse_args()
ARG_OUTPUT = args.output
ARG_CASE = args.case
ARG_METHOD = args.method
ARG_TIMEOUT = args.timeout
ARG_STEP = args.step
ARG_INDEX = args.index

# print args
print('Output:', ARG_OUTPUT)
print('Case:', ARG_CASE)
print('Method:', ARG_METHOD)
print('Timeout:', ARG_TIMEOUT)
print('Step:', ARG_STEP)
print('Index:', ARG_INDEX)


DATASET = 'data6'


class TestMethod(Enum):
    AHP = 'ah+'
    AH = 'ah'
    BFS = 'bfs'


class TestCase:
    def __init__(self, case_name: str, step_name: str,
                 method: TestMethod,
                 src_plan: QueryPlan, dst_plan: QueryPlan):
        self.case_name = case_name
        self.step_name = step_name
        self.method = method
        self.src_plan = src_plan
        self.dst_plan = dst_plan

    def get_question_str(self):
        return f'{self.case_name} {self.step_name}'


def main():
    test_cases = prepare_test_cases()
    evaluate(test_cases)
    print('Done')


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


def prepare_test_cases() -> list[TestCase]:
    result_path = os.path.join(ROOT_PATH, 'data', DATASET, 'result')

    case_names = os.listdir(result_path)
    case_names = list(filter(lambda x: not x.startswith('.'), case_names))

    # filter the case
    case_names = list(filter(lambda x: re.match(ARG_CASE, x), case_names))
    if not case_names:
        print('Case not found')
        return []

    case_names.sort()

    test_cases = []
    for case_name in case_names:
        case_path = os.path.join(result_path, case_name, 'trace.json')

        print('Prepare test case for:', case_name)

        if not os.path.exists(case_path):
            print(case_path, 'trace.json not exists')
            continue

        # plans

        obj = read_json_obj(case_path)
        trace = Trace.load(obj)
        raw_plans = trace.plans

        if not ARG_STEP and not ARG_INDEX:
            start_idx, end_idx = trace.trace_tree.find_step_plan_indices('Optimization')
        elif ARG_STEP:
            start_idx, end_idx = trace.trace_tree.find_step_plan_indices(ARG_STEP)
            if start_idx == -1:
                print('Step not found')
                continue
        elif ARG_INDEX:
            start_idx, end_idx = ARG_INDEX, ARG_INDEX + 1
        else:
            raise Exception('Invalid arguments')

        parser = PlanParser()
        selected_raw_plans = raw_plans[start_idx:end_idx+1]
        plans = [parser.parse(p) for p in selected_raw_plans]

        # method
        methods: list[TestMethod] = []
        for method in TestMethod.__members__.values():
            if re.match(ARG_METHOD, method.value):
                methods.append(method)

        for i in range(len(plans) - 1):
            src_plan = plans[i]
            dst_plan = plans[i + 1]
            step_name = trace.trace_tree.find_minimum_step_by_start_idx(start_idx + i).name
            for method in methods:
                test_cases.append(TestCase(case_name, step_name, method, src_plan, dst_plan))

    return test_cases


def evaluate(cases: list[TestCase]):
    ahp_status_dict: dict[str, AlgoStatus] = {}
    for test_case in cases:
        print(f'=== Evaluate {test_case.case_name} {test_case.step_name} {test_case.method.value} ===')

        case_problem = test_case.get_question_str()
        if case_problem in ahp_status_dict:
            if ahp_status_dict[case_problem] != AlgoStatus.SUCCESS:
                print('skip as AHP result is ', ahp_status_dict[case_problem])
                continue
        else:
            # no ahp record. execute
            pass

        p0, p1 = test_case.src_plan, test_case.dst_plan
        src_plan_node_cnt = len(p0.node_dict)
        dst_plan_node_cnt = len(p1.node_dict)

        if test_case.method == TestMethod.BFS:
            extractor = TransPathSearcherBFS(p0, p1, RULE_LIST, ARG_TIMEOUT)
            try:
                with HiddenPrints():
                    rule_path = extractor.execute()
            except Exception as e:
                sys.stderr.write(f'Test case failed: {e}')
                sys.stderr.write(traceback.format_exc())
                continue
            path_len = len(rule_path) if rule_path else -1
            status = extractor.status
            time_cost = extractor.get_time_cost()
            explored_cnt = extractor.attempt_count
            generated_cnt = extractor.generated_plan_count

        elif test_case.method == TestMethod.AH:
            extractor = TransPathSearcherAH(p0, p1, RULE_LIST, timeout=1800)
            extractor.precompute()
            try:
                with HiddenPrints():
                    rule_path = extractor.execute()
            except Exception as e:
                sys.stderr.write(f'Test case failed: {e}')
                sys.stderr.write(traceback.format_exc())
                continue
            path_len = len(rule_path) if rule_path else -1
            status = extractor.status
            time_cost = extractor.get_time_cost()
            explored_cnt = extractor.attempt_count
            generated_cnt = extractor.generated_plan_count

        elif test_case.method == TestMethod.AHP:
            # extractor = TransPathSearcherAHP(p0, p1, NORMAL_RULE_LIST, REORDER_RULE_LIST, normal_timeout=ARG_TIMEOUT)
            extractor = TransPathSearcherAHP(p0, p1, RULE_LIST, timeout=1800)
            extractor.precompute()
            try:
                with HiddenPrints():
                    rule_path = extractor.execute()
            except Exception as e:
                sys.stderr.write(f'Test case failed: {e}')
                sys.stderr.write(traceback.format_exc())
                continue
            path_len = len(rule_path) if rule_path else -1
            status = extractor.status
            time_cost = extractor.get_time_cost()
            explored_cnt = extractor.attempt_count
            generated_cnt = extractor.generated_plan_count

            ahp_status_dict[case_problem] = status

        else:
            raise Exception('Invalid method')

        append_record([
            # timestamp
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            test_case.case_name, test_case.step_name, test_case.method.value,
            src_plan_node_cnt, dst_plan_node_cnt, path_len,
            status, time_cost, explored_cnt, generated_cnt
        ])


def append_record(row):
    # header
    # timestamp	case	step name	method
    # src plan node #	dst plan node #	path length
    # status	time cost (ms)	explored plan #	generated plan #
    # timeout
    if not os.path.exists(ARG_OUTPUT):
        with open(ARG_OUTPUT, 'w') as f:
            f.write('timestamp,case,step name,method,'
                    'src plan node #,dst plan node #,path length,'
                    'status,time cost (ms),explored plan #,generated plan #,'
                    'timeout\n')
    with open(ARG_OUTPUT, 'a') as f:
        f.write(','.join(map(str, row + [ARG_TIMEOUT])) + '\n')


if __name__ == '__main__':
    main()
