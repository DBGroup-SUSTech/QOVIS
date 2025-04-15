class Fragment2Set:
    OFFSET = 1000
    ANY = '*'

    def __init__(self, known_fragments: list[tuple[str, str]] = None):
        self.counter: dict[tuple[str, str], int] = {}
        self.parent_kind_dict: dict[str, set[tuple[str, str]]] = {}  # parent_kind -> (parent_kind, child_kind)
        self.child_kind_dict: dict[str, set[tuple[str, str]]] = {}  # child_kind -> (parent_kind, child_kind)
        if known_fragments:
            self.register(*known_fragments)

    def register(self, *fragments: tuple[str, str]):
        """ Register a fragment to the set """
        for fragment in fragments:
            self.set(fragment, 0)
            self.parent_kind_dict.setdefault(fragment[0], set()).add(fragment)
            self.child_kind_dict.setdefault(fragment[1], set()).add(fragment)

    def set(self, fragment: tuple[str, str], multiplicity: int):
        """ Set multiplicity of a given fragment (no wildcard considered) """
        # assert len(fragment) == 2, 'fragment must be a tuple of length 2'
        self.counter[fragment] = multiplicity

    def add(self, fragment: tuple[str, str], multiplicity: int = 1):
        """ Add a fragment to the set and increment multiplicity for it """
        # assert len(fragment) == 2, 'fragment must be a tuple of length 2'
        # # no wildcard
        # assert all(kind != self.ANY for kind in fragment), 'fragment cannot have wildcard'
        # increment multiplicity for the fragment itself
        if fragment in self.counter:
            self.counter[fragment] += multiplicity

    def count(self, fragment: tuple[str, str]) -> int:
        """ Get multiplicity of a given fragment """
        # assert len(fragment) == 2, 'fragment must be a tuple of length 2'
        # # no wildcard
        # assert all(kind != self.ANY for kind in fragment), 'fragment cannot have wildcard'
        return self.counter.get(fragment, 0)

    def add_with_wildcard(self, fragment: tuple[str, str], multiplicity: int = 1):
        """ Add a fragment to the set and increment multiplicity for it """
        # assert len(fragment) == 2, 'fragment must be a tuple of length 2'
        fragments = {fragment}
        if self.ANY in fragment:
            # assert fragment[0] != self.ANY or fragment[1] != self.ANY, 'fragment cannot have wildcard at 2 positions'
            if fragment[0] == self.ANY and fragment[1] in self.child_kind_dict:
                for saved_fragment in self.child_kind_dict[fragment[1]]:
                    fragments.add(saved_fragment)
            elif fragment[1] == self.ANY and fragment[0] in self.parent_kind_dict:
                for saved_fragment in self.parent_kind_dict[fragment[0]]:
                    fragments.add(saved_fragment)

        for fragment in fragments:
            self.add(fragment, multiplicity)

    def add_all(self, fragments: list[tuple[str, str]], multiplicity: int = 1):
        """ Add fragment without duplication """
        fragment_set = set()
        for fragment in fragments:
            if Fragment2Set.ANY in fragment:
                if fragment[0] == self.ANY and fragment[1] in self.child_kind_dict:
                    for saved_fragment in self.child_kind_dict[fragment[1]]:
                        fragment_set.add(saved_fragment)
                elif fragment[1] == self.ANY and fragment[0] in self.parent_kind_dict:
                    for saved_fragment in self.parent_kind_dict[fragment[0]]:
                        fragment_set.add(saved_fragment)
            else:
                fragment_set.add(fragment)

        for fragment in fragment_set:
            self.add(fragment, multiplicity)

    # def add(self, fragment: tuple[str, str], multiplicity: int = 1):
    #     """ Add a fragment to the set and increment multiplicity for it and its wildcard counterparts (if any) """
    #     assert len(fragment) == 2, 'fragment must be a tuple of length 2'
    #     # not all the element is wildcard
    #     assert any(kind != Fragment2Set.ANY for kind in fragment), 'fragment cannot be all wildcard'
    #
    #     # increment multiplicity for the fragment itself
    #     if fragment in self.counter:
    #         self.counter[fragment] += multiplicity
    #     if self.ANY not in fragment:
    #         # increment multiplicity for wildcard counterparts
    #         for i in range(2):
    #             wildcard_fragment = list(fragment)
    #             wildcard_fragment[i] = Fragment2Set.ANY
    #             wildcard_fragment = tuple(wildcard_fragment)
    #             if wildcard_fragment in self.counter:
    #                 self.counter[wildcard_fragment] += multiplicity
    #
    # def count(self, fragment: tuple[str, str]) -> int:
    #     """ Get multiplicity of a given fragment AND its wildcard counterparts (if any) """
    #     assert len(fragment) == 2, 'fragment must be a tuple of length 2'
    #     # not all the element is wildcard
    #     assert any(kind != Fragment2Set.ANY for kind in fragment), 'fragment cannot be all wildcard'
    #
    #     result = self.counter.get(fragment, 0)
    #     if self.ANY not in fragment:
    #         for i in range(2):
    #             wildcard_fragment = list(fragment)
    #             wildcard_fragment[i] = Fragment2Set.ANY
    #             wildcard_fragment = tuple(wildcard_fragment)
    #             result += self.counter.get(wildcard_fragment, 0)
    #     return result

