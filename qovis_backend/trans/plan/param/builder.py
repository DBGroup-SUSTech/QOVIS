from enum import Enum
from typing import Union, Optional

from trans.plan.param.base_param import BaseParam


class Builder:
    class Kind(Enum):
        # attrs
        ATTRS_UNION = 0
        ATTRS_INTERSECT = 1
        ATTRS_RENAME = 2
        # exprs
        COLLAPSE_TO = 3
        ATTRS_AS_EXPRS = 4
        # rel
        ATTRS_AS_REL = 5

    def __init__(self, kind: Kind,
                 left: Union[BaseParam, 'Builder'],
                 right: Union[BaseParam, 'Builder', None]):
        self.kind = kind
        self.left = left
        self.right = right

    def compute(self, sym2value: dict[BaseParam, BaseParam]) -> BaseParam:
        raise NotImplementedError()

    def get_or_compute(self,
                       param_or_builder: Union[BaseParam, 'Builder', None],
                       sym2value: dict[BaseParam, BaseParam]) -> Optional[BaseParam]:
        if param_or_builder is None:
            return None
        if issubclass(param_or_builder.__class__, BaseParam):
            return sym2value[param_or_builder]
        assert issubclass(param_or_builder.__class__, Builder)
        return param_or_builder.compute(sym2value)

    def collect_symbols(self) -> list[BaseParam]:
        res = []
        if issubclass(self.left.__class__, BaseParam):
            res.append(self.left)
        else:
            res += self.left.collect_symbols()
        if self.right is not None:
            if issubclass(self.right.__class__, BaseParam):
                res.append(self.right)
            else:
                res += self.right.collect_symbols()
        return res

