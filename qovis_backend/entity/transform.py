from enum import Enum
from typing import Optional


class TransType(Enum):
    INSERT = 'insert'
    DELETE = 'delete'
    REPLACE = 'replace'
    MODIFY = 'modify'
    UNCHANGE = 'unchange'


class Transform:
    def __init__(self, src_vid: Optional[int], dst_vid: Optional[int], type_: TransType):
        self.src_vid: Optional[int] = src_vid
        self.dst_vid: Optional[int] = dst_vid
        self.type: TransType = type_

    def dump(self):
        return {
            'srcVid': self.src_vid,
            'dstVid': self.dst_vid,
            'type': self.type.value,
        }

    @staticmethod
    def load(data):
        return Transform(
            src_vid=data['srcVid'],
            dst_vid=data['dstVid'],
            type_=TransType(data['type']),
        )

    def __repr__(self):
        return f'{self.type.value} {self.src_vid} -> {self.dst_vid}'
