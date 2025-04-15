import os
import sys
import time

from entity.trace import Trace
from entity.trace_tree import TraceNode, ProcType
from utils.common_io import read_json_obj, write_csv

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)


def statistics_operators(trace: Trace):
    start_time = time.time()

    plans = trace.plans
    trace_tree = trace.trace_tree

    # compute all phase name and end index
    phase_names = []
    end_indices = []
    for node in trace_tree.root.children:
        phase_names.append(node.name)
        end_indices.append(node.end_idx)

    # count operators
    # clazz -> {short_name: str, count: int}
    tot_operator_data = {}
    for plan in plans:
        for node in plan.node_dict.values():
            clazz = node.clazz
            if clazz not in tot_operator_data:
                tot_operator_data[clazz] = {'short_name': node.name, 'count': 0}
            tot_operator_data[clazz]['count'] += 1

    # count operators in each phase
    # phase -> {clazz -> {short_name: str, count: int}}
    operator_data = {}
    cur_phase_idx = 0
    for i, plan in enumerate(plans):
        phase_dict = operator_data.setdefault(phase_names[cur_phase_idx], {})
        for node in plan.node_dict.values():
            clazz = node.clazz
            if clazz not in phase_dict:
                phase_dict[clazz] = {'short_name': node.name, 'count': 0}
            phase_dict[clazz]['count'] += 1
        if i >= end_indices[cur_phase_idx]:
            cur_phase_idx += 1

    end_time = time.time()
    print('time:', end_time - start_time)

    return tot_operator_data, operator_data


def statistics_rules(trace: Trace):
    start_time = time.time()

    trace_tree = trace.trace_tree

    # get all leaf nodes of trace tree and phases
    leaf_nodes: list[(TraceNode, str)] = []

    def dfs(node_: TraceNode, cur_phase: str):
        if cur_phase == '' and node_.type == ProcType.Phase.value:
            cur_phase = node_.name
        if node_.children:
            for child in node_.children:
                dfs(child, cur_phase)
        else:
            leaf_nodes.append((node_, cur_phase))
    dfs(trace_tree.root, '')

    # count rules
    # name -> count
    tot_rule_data = {}
    for node, phase in leaf_nodes:
        rule_name = node.name
        if rule_name not in tot_rule_data:
            tot_rule_data[rule_name] = 0
        tot_rule_data[rule_name] += 1

    # count rules in each phase
    # phase -> {name -> count}
    phase_rule_data = {}
    for node, phase in leaf_nodes:
        rule_name = node.name
        if phase not in phase_rule_data:
            phase_rule_data[phase] = {}
        if rule_name not in phase_rule_data[phase]:
            phase_rule_data[phase][rule_name] = 0
        phase_rule_data[phase][rule_name] += 1

    end_time = time.time()
    print('time:', end_time - start_time)

    return tot_rule_data, phase_rule_data


def main():
    dataset = 'data5'

    proc_path = os.path.join(ROOT_PATH, 'data', dataset, 'proc')
    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')

    example_list = os.listdir(proc_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    # example_list = list(filter(lambda x: x.startswith('ssb'), example_list))
    # example_list = list(filter(lambda x: x.startswith('bug'), example_list))
    example_list.sort()

    # example_list = ['ssb-q1']
    # example_list = [f"ssb-q{i}" for i in range(1, 14)]

    phase_operator_data = {}
    tot_operator_data = {}
    phase_rule_data = {}
    tot_rule_data = {}

    for example_name in example_list:
        filepath = os.path.join(result_path, example_name, 'trace.json')

        if not os.path.exists(filepath):
            print(example_name, 'trace.json not exists')
            continue

        print(example_name, 'analyzing...')

        obj = read_json_obj(filepath)
        trace = Trace.load(obj)

        ex_tot_operator_data, ex_phase_operator_data = statistics_operators(trace)
        for clazz, data in ex_tot_operator_data.items():
            if clazz not in tot_operator_data:
                tot_operator_data[clazz] = data
            else:
                tot_operator_data[clazz]['count'] += data['count']
        for phase, clazz_data in ex_phase_operator_data.items():
            if phase not in phase_operator_data:
                phase_operator_data[phase] = {}
            for clazz, data in clazz_data.items():
                if clazz not in phase_operator_data[phase]:
                    phase_operator_data[phase][clazz] = data
                else:
                    phase_operator_data[phase][clazz]['count'] += data['count']

        ex_tot_rule_data, ex_phase_rule_data = statistics_rules(trace)
        for rule_name, count in ex_tot_rule_data.items():
            if rule_name not in tot_rule_data:
                tot_rule_data[rule_name] = count
            else:
                tot_rule_data[rule_name] += count
        for phase, rule_data in ex_phase_rule_data.items():
            if phase not in phase_rule_data:
                phase_rule_data[phase] = {}
            for rule_name, count in rule_data.items():
                if rule_name not in phase_rule_data[phase]:
                    phase_rule_data[phase][rule_name] = count
                else:
                    phase_rule_data[phase][rule_name] += count

        print()

    # print(phase_operator_data)
    # print(tot_operator_data)
    # print(phase_rule_data)
    # print(tot_rule_data)

    # save data as csv
    analysis_path = os.path.join(ROOT_PATH, 'data', dataset, 'analysis')
    if not os.path.exists(analysis_path):
        os.makedirs(analysis_path)

    # phase operator
    lines = [['phase', 'clazz', 'short_name', 'count']]
    for phase, clazz_data in phase_operator_data.items():
        for clazz, data in clazz_data.items():
            lines.append([phase, clazz, data['short_name'], data['count']])

    write_csv(os.path.join(analysis_path, 'phase_operator.csv'), lines)

    # tot operator
    lines = [['clazz', 'short_name', 'count']]
    for clazz, data in tot_operator_data.items():
        lines.append([clazz, data['short_name'], data['count']])
    write_csv(os.path.join(analysis_path, 'tot_operator.csv'), lines)

    # phase rule
    lines = [['phase', 'rule_name', 'count']]
    for phase, rule_data in phase_rule_data.items():
        for rule_name, count in rule_data.items():
            lines.append([phase, rule_name, count])
    write_csv(os.path.join(analysis_path, 'phase_rule.csv'), lines)

    # tot rule
    lines = [['rule_name', 'count']]
    for rule_name, count in tot_rule_data.items():
        lines.append([rule_name, count])
    write_csv(os.path.join(analysis_path, 'tot_rule.csv'), lines)


if __name__ == '__main__':
    main()
