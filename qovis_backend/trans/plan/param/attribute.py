class Attribute:
    def __init__(self, str_: str = ""):
        self.str = str_.strip()

        self.name: str = ""
        self.id: int = -1
        self.suffix: str = ""
        self.undefined = False

        if self.str == "":
            self.undefined = True
        else:
            self._init_from_str()

    def _init_from_str(self):
        arr = self.str.split("#")
        self.name = arr[0]
        self.suffix = 'L' if 'L' in arr[1] else ''
        self.id = int(arr[1].replace("L", ""))

    def __str__(self):
        return f"{self.name}#{self.id}{self.suffix}" if not self.undefined else "<undefined attr>"

    def __repr__(self):
        return self.__str__()

    def to_hash_str(self):
        return self.name

    def to_unique_str(self):
        return str(self)

    def equals(self, other):
        """ Compare directly without finding reference. """
        if not isinstance(other, Attribute):
            return False
        return self.name == other.name and self.id == other.id

    def copy(self) -> 'Attribute':
        attr = Attribute(self.str)
        attr.name = self.name
        attr.id = self.id
        attr.suffix = self.suffix
        return attr

