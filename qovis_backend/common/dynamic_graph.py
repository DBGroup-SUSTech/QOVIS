from typing import List, Dict

from common.plan import Plan


class DynamicGraph:
    def __init__(self):
        self.query_name = 'unknown'
        self.plans: List[Plan] = []
        self.phase_intervals: List[(int, int)] = []
        self.phase_names: List[str] = []

    def dump(self) -> Dict:
        return {
            'queryName': self.query_name,
            'plans': [p.dump() for p in self.plans],
            'phaseIntervals': self.phase_intervals,
            'phaseNames': self.phase_names,
        }

    @staticmethod
    def load(dct: Dict):
        dg = DynamicGraph()
        dg.plans = dct['queryName']
        dg.plans = [Plan.load(p) for p in dct['plans']]
        dg.phase_intervals = dct['phaseIntervals']
        dg.phase_names = dct['phaseNames']
        return dg
