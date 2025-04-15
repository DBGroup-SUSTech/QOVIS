from typing import Optional, Union

from trans.plan.param.attribute import Attribute
from trans.plan.param.attributes import Attributes, AttrsBuilder
from trans.plan.param.base_param import BaseParam
from trans.plan.param.builder import Builder
from trans.plan.param.expressions import Expressions
from utils.id_counter import IdCounter


class Relation(BaseParam):
    Counter = IdCounter(1)

    def __init__(self):
        super().__init__(BaseParam.Kind.REL)
        self.id: int = Relation.Counter.get()
        self.name: str = 'Rel'
        self.attrs = Attributes().set_owner_rel(self)       # all attributes are Kind.COLUMN
        self.is_empty: bool = False

    def __repr__(self):
        return f"{self.name}({self.id}){'<empty>' if self.is_empty else ''}{self.attrs.items}"

    def to_hash_str(self) -> str:
        return f"{self.name}({self.attrs.to_hash_str()})"

    def get_attr_list(self) -> list[str]:
        return list(map(lambda a: a.str, self.attrs.items))

    def copy(self) -> 'Relation':
        rel = Relation()
        rel.init_from(self)
        return rel

    def copy_with_new_id(self) -> 'Relation':
        rel = Relation()
        rel.init_from_with_new_id(self)
        return rel

    def equals(self, other):
        if not isinstance(other, Relation):
            return False
        return self.id == other.id

    def semantically_equals(self, other):
        if not isinstance(other, Relation):
            return False
        return self.name == other.name \
               and self.attrs.semantically_equals(other.attrs) \
               and self.is_empty == other.is_empty

    def includes_attr(self, attr: Attribute):
        return self.attrs.includes(attr)

    def init(self, name: str, attrs: list[Attribute], is_empty: bool = False) -> 'Relation':
        self.name = name
        self.attrs.init(attrs)\
            .set_owner_rel(self)
        self.is_empty = is_empty
        self.inited = True
        return self

    def init_from(self, rel: 'Relation') -> 'Relation':
        self.id = rel.id
        self.name = rel.name
        self.attrs.init_from(rel.attrs)\
            .set_owner_rel(self)
        self.is_empty = rel.is_empty
        self.inited = True
        return self

    def init_from_with_new_id(self, rel: 'Relation') -> 'Relation':
        self.id = Relation.Counter.get()
        self.name = rel.name
        self.attrs.init_from(rel.attrs)\
            .set_owner_rel(self)
        self.is_empty = rel.is_empty
        self.inited = True
        return self

    def set_attrs_from(self, attrs: Attributes) -> 'Relation':
        self.attrs.init_from(attrs)\
            .set_owner_rel(self)
        return self

    def set_attrs_from_list(self, attrs: list[Attribute]) -> 'Relation':
        self.attrs.init(attrs)\
            .set_owner_rel(self)
        return self

    def set_is_empty(self, is_empty: bool) -> 'Relation':
        self.is_empty = is_empty
        return self

    def find_attr(self, attr: Attribute) -> Optional[Attribute]:
        return self.attrs.find(attr)

    def get_index(self) -> Optional[int]:
        if self.owner is None:
            return None
        return self.owner.params[BaseParam.Kind.REL].index(self)


class RelBuilder(Builder):
    def __init__(self, kind: Builder.Kind,
                 attrs: Union[Attributes, AttrsBuilder, None]):
        super().__init__(kind, attrs, None)

    def compute(self, sym2value: dict[BaseParam, BaseParam]) -> Relation:
        attrs = self.get_or_compute(self.left, sym2value)

        if self.kind == RelBuilder.Kind.ATTRS_AS_REL:
            assert isinstance(attrs, Attributes)
            return Relation().init('Rel', attrs.items)
        else:
            raise Exception(f"Unknown RelBuilder.Kind: {self.kind}")


def as_rel_immediately(attrs: Attributes) -> Relation:
    return Relation().init('Rel', attrs.items)


def as_rel(attrs: Union[Attributes, AttrsBuilder]) -> RelBuilder:
    return RelBuilder(RelBuilder.Kind.ATTRS_AS_REL, attrs)


def __inner_test():
    pe0 = Expressions()
    pr0 = Relation()

    builder = as_rel(pr0.attrs.rename(pe0))

    e0 = Expressions().init_from_str("a#1 AS b#2, c#3")
    r0 = Relation().init("Rel", [Attribute("a#1"), Attribute("c#3")])
    # results:  Rel[b#2, c#3]

    sym2params = {pe0: e0, pr0.attrs: r0.attrs}
    print(builder.compute(sym2params))


if __name__ == '__main__':
    __inner_test()
