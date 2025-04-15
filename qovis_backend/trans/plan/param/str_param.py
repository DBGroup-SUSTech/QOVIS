from trans.plan.param.base_param import BaseParam


class StrParam(BaseParam):
    def __init__(self):
        super().__init__(BaseParam.Kind.STR)
        self.value: str = ""

    def init(self, value: str) -> 'StrParam':
        self.value = value
        self.inited = True
        return self

    def init_from(self, other: 'StrParam') -> 'StrParam':
        self.value = other.value
        self.inited = True
        return self

    def copy(self) -> 'StrParam':
        return StrParam().init_from(self)

    def equals(self, other):
        if not isinstance(other, StrParam):
            return False
        return self.value == other.value

    def semantically_equals(self, other):
        return self.equals(other)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)

    def to_hash_str(self) -> str:
        return self.value
