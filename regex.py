from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    next_states: list[State]

    @abstractmethod
    def __init__(self) -> None:
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass


class TerminationState(State):
    """
    state for death
    """
    def __init__(self) -> None:
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, char: str) -> bool:
        return char == self.curr_sym


class StarState(State):
    """
    state for * character
    """
    def __init__(self, inner: State):
        super().__init__()
        self.inner = inner
        inner.next_states.append(self)
        self.next_states = [inner]

    def check_self(self, char: str) -> bool:
        return self.inner.check_self(char)


class PlusState(State):
    """
    state for + character 
    """
    def __init__(self, inner: State):
        super().__init__()
        self.inner = inner
        inner.next_states.append(self)
        self.next_states = [inner]

    def check_self(self, char: str) -> bool:
        return self.inner.check_self(char)


class StartState(State):
    """
    state for start
    """
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False


class RegexFSM:
    """
    regex for poor
    """
    def __init__(self, regex_expr: str) -> None:
        self.start = StartState()
        states_chain: list[State] = [self.start]
        preds: list[State | None] = [None]

        i = 0
        while i < len(regex_expr):
            c = regex_expr[i]

            if c == ".":
                node = DotState()

            elif c.isascii() and c not in "*+":
                node = AsciiState(c)

            elif c in "*+":
                if len(states_chain) < 2:
                    raise ValueError(f"Nothing to repeat with '{c}' at pos {i}")
                inner = states_chain.pop()
                parent = preds.pop()
                if c == "*":
                    node = StarState(inner)
                else:
                    node = PlusState(inner)
                if parent is not None:
                    for idx, nxt in enumerate(parent.next_states[::-1], 1):
                        if nxt is inner:
                            parent.next_states[-idx] = node
                            break
                else:
                    self.start.next_states = [node if x is inner else x for x in self.start.next_states]
                states_chain.append(node)
                preds.append(parent)
                i += 1
                continue

            else:
                raise AttributeError(f"Unsupported character '{c}'")

            parent = states_chain[-1]
            parent.next_states.append(node)
            states_chain.append(node)
            preds.append(parent)

            i += 1

        term = TerminationState()
        parent = states_chain[-1]
        parent.next_states.append(term)
        self.final = term
        self.start_state = self.start

    def check_string(self, s: str) -> bool:
        """
        scans the string for regex inconsistencies 
        """
        def dfs(state: State, idx: int) -> bool:
            if isinstance(state, TerminationState):
                return idx == len(s)
            if idx < len(s) and state.check_self(s[idx]):
                for nxt in state.next_states:
                    if dfs(nxt, idx + 1):
                        return True
            if isinstance(state, (StarState, PlusState)):
                for nxt in state.next_states:
                    if dfs(nxt, idx):
                        return True
            return False

        for nxt in self.start.next_states:
            if dfs(nxt, 0):
                return True
        return False


if __name__ == "__main__":
    tests = [
        ("a*a", "a", True),
        ("a*4.+hi", "4uhi", True),
        ("a*4.+hi", "meow", False),
        ("m*..+w", "meow", True),
        ("m*..+w", "meovalw", True),
        ("m*..+w", "eow", True),
    ]
    for pattern, string, expected in tests:
        fsm = RegexFSM(pattern)
        result = fsm.check_string(string)
        print(f"{pattern!r} * {string!r} = {result} (expected {expected})")
