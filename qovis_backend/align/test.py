from align.tree_align_algo import TreeAlignAlgo
from entity.plan import PlanNode, Plan, PlanEdge


def link_parent_child(plan: Plan, parent: PlanNode, child: PlanNode):
    edge = PlanEdge(child, parent, '')
    plan.edge_dict[edge.eid] = edge
    parent.providers.append(child)
    child.consumers.append(parent)


def get_plan0():
    scan = PlanNode('TableScan', '', 0, 'TableScan#0', 0, ['a#0'])

    plan = Plan(0)
    plan.root = scan
    plan.node_dict = {v.vid: v for v in [scan]}

    return plan


def get_plan1():
    scan = PlanNode('InMemoryScan', '', 1, 'InMemoryScan#1', 0, ['a#0'])

    plan = Plan(1)
    plan.root = scan
    plan.node_dict = {v.vid: v for v in [scan]}

    return plan


def get_plan2():
    proj = PlanNode('Project', '', 0, 'Project', 0, ['a#0', 'b#1'])
    join = PlanNode('Hash Join', '', 1, 'Hash Join', 0, ['a#0 = b#1'])
    scan1 = PlanNode('TableScan', '', 2, 'TableScan', 0, ['a#0'])
    scan2 = PlanNode('TableScan', '', 3, 'TableScan', 0, ['b#1'])

    plan = Plan(1)
    plan.root = proj
    plan.node_dict = {v.vid: v for v in [proj, join, scan1, scan2]}

    link_parent_child(plan, proj, join)
    link_parent_child(plan, join, scan1)
    link_parent_child(plan, join, scan2)

    return plan


def get_plan3():
    proj = PlanNode('Project', '', 0, 'Project', 0, ['a#0', 'b#1'])
    join = PlanNode('Sort Merge Join', '', 1, 'Sort Merge Join', 0, ['a#0 = b#1'])
    scan1 = PlanNode('TableScan', '', 2, 'TableScan', 0, ['a#0'])
    scan2 = PlanNode('TableScan', '', 3, 'TableScan', 0, ['b#1'])

    plan = Plan(2)
    plan.root = proj
    plan.node_dict = {v.vid: v for v in [proj, join, scan1, scan2]}

    link_parent_child(plan, proj, join)
    link_parent_child(plan, join, scan1)
    link_parent_child(plan, join, scan2)

    return plan


def get_plan4():
    proj = PlanNode('Project', '', 0, 'Project', 0, ['a#0', 'b#1'])
    filter_ = PlanNode('Filter', '', 4, 'Filter', 0, ['a#0 = 0'])
    join = PlanNode('Sort Merge Join', '', 1, 'Sort Merge Join', 0, ['a#0 = b#1'])
    scan1 = PlanNode('TableScan', '', 2, 'TableScan', 0, ['a#0'])
    scan2 = PlanNode('TableScan', '', 3, 'TableScan', 0, ['b#1'])

    plan = Plan(3)
    plan.root = proj
    plan.node_dict = {v.vid: v for v in [proj, filter_, join, scan1, scan2]}

    link_parent_child(plan, proj, filter_)
    link_parent_child(plan, filter_, join)
    link_parent_child(plan, join, scan1)
    link_parent_child(plan, join, scan2)

    return plan


def get_test_cases():
    cases = [
        (get_plan0(), get_plan0(), 0),
        (get_plan0(), get_plan1(), 1),
        (get_plan2(), get_plan3(), 1),
        (get_plan2(), get_plan4(), 2),
    ]

    return cases


def main():
    for i, case in enumerate(get_test_cases()):
        plan1, plan2, cost = case
        print(f'Test case {i}:')
        print(f'plan1: {plan1}')
        print(f'plan2: {plan2}')
        print(f'expected cost: {cost}')

        algo = TreeAlignAlgo(plan1, plan2)
        algo.exec()

        actual = algo.min_cost

        print(f'actual cost: {actual}')

        assert actual == cost

        print(algo.get_align_tree().to_tree_str())

        print()


if __name__ == '__main__':
    main()
