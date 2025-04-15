from enum import Enum


class SortOrder(Enum):
    ASC = 1
    DESC = 2

    @classmethod
    def from_str(cls, s: str) -> 'SortOrder':
        if s == "ASC":
            return cls.ASC
        elif s == "DESC":
            return cls.DESC
        else:
            raise ValueError(f"Invalid sort order: {s}")


class NullOrder(Enum):
    FIRST = 1
    LAST = 2

    @classmethod
    def from_str(cls, s: str) -> 'NullOrder':
        if s == "NULLS FIRST":
            return cls.FIRST
        elif s == "NULLS LAST":
            return cls.LAST
        else:
            raise ValueError(f"Invalid null order: {s}")
