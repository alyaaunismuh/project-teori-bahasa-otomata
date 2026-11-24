"""
Program NFA, DFA, dan Konversi NFA ke DFA (Subset Construction)
Mendukung epsilon-transition (simbol '' / EPS).
"""

from collections import deque

EPS = ""  # simbol epsilon


# ===================== DFA =====================
class DFA:
    def __init__(self, states, alphabet, transitions, start, finals):
        self.states = states            # set of state
        self.alphabet = alphabet        # set of simbol
        self.transitions = transitions  # dict: (state, simbol) -> state
        self.start = start
        self.finals = finals

    def accepts(self, string):
        state = self.start
        for ch in string:
            if (state, ch) not in self.transitions:
                return False
            state = self.transitions[(state, ch)]
        return state in self.finals

    def print_table(self):
        print_table(self.states, sorted(self.alphabet), self.start, self.finals,
                    lambda s, a: self.transitions.get((s, a), "-"))


# ===================== NFA =====================
class NFA:
    def __init__(self, states, alphabet, transitions, start, finals):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # dict: (state, simbol) -> set of state
        self.start = start
        self.finals = finals

    def epsilon_closure(self, states):
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            for t in self.transitions.get((s, EPS), set()):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return frozenset(closure)

    def move(self, states, symbol):
        result = set()
        for s in states:
            result |= self.transitions.get((s, symbol), set())
        return result

    def accepts(self, string):
        current = self.epsilon_closure({self.start})
        for ch in string:
            current = self.epsilon_closure(self.move(current, ch))
        return bool(current & self.finals)

    def print_table(self):
        symbols = sorted(self.alphabet) + ([EPS] if any(k[1] == EPS for k in self.transitions) else [])
        print_table(self.states, symbols, self.start, self.finals,
                    lambda s, a: fmt_set(self.transitions.get((s, a), set())))

    # ---------- Konversi NFA -> DFA (Subset Construction) ----------
    def to_dfa(self):
        start = self.epsilon_closure({self.start})
        dfa_states, dfa_trans, dfa_finals = {start}, {}, set()
        queue = deque([start])

        while queue:
            current = queue.popleft()
            if current & self.finals:
                dfa_finals.add(current)
            for a in sorted(self.alphabet):
                target = self.epsilon_closure(self.move(current, a))
                if not target:
                    continue  # tidak ada transisi (dead state tidak ditampilkan)
                dfa_trans[(current, a)] = target
                if target not in dfa_states:
                    dfa_states.add(target)
                    queue.append(target)

        # Ganti himpunan state dengan label ringkas, misal {q0,q1}
        label = {s: fmt_set(s) for s in dfa_states}
        return DFA(
            {label[s] for s in dfa_states},
            set(self.alphabet),
            {(label[s], a): label[t] for (s, a), t in dfa_trans.items()},
            label[start],
            {label[s] for s in dfa_finals},
        )


# ===================== Util =====================
def fmt_set(states):
    if isinstance(states, str):
        return states
    return "{" + ",".join(sorted(states)) + "}" if states else "-"


def print_table(states, symbols, start, finals, cell):
    w = max(14, max(len(s) for s in states) + 4)
    print(f"{'State':<{w}}" + "".join(f"{(a or 'ε'):<{w}}" for a in symbols))
    print("-" * (w * (len(symbols) + 1)))
    for s in sorted(states):
        mark = ("->" if s == start else "  ") + ("*" if s in finals else " ")
        print(f"{mark + s:<{w}}" + "".join(f"{cell(s, a):<{w}}" for a in symbols))
    print("(-> = start state, * = final state)\n")


# ===================== Main =====================
def main():
    # Contoh: NFA yang menerima string {a,b} yang berakhiran "ab"
    nfa = NFA(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        transitions={
            ("q0", "a"): {"q0", "q1"},
            ("q0", "b"): {"q0"},
            ("q1", "b"): {"q2"},
        },
        start="q0",
        finals={"q2"},
    )

    print("=== TABEL TRANSISI NFA ===")
    nfa.print_table()

    dfa = nfa.to_dfa()
    print("=== TABEL TRANSISI DFA (hasil konversi) ===")
    dfa.print_table()

    print("=== PENGUJIAN STRING ===")
    print(f"{'String':<12}{'NFA':<10}{'DFA':<10}")
    for s in ["ab", "aab", "bab", "abb", "ba", "", "abab", "aabb"]:
        print(f"{repr(s):<12}{str(nfa.accepts(s)):<10}{str(dfa.accepts(s)):<10}")

    # Mode interaktif
    print("\nKetik string untuk diuji (kosongkan untuk keluar):")
    while True:
        s = input("> ").strip()
        if not s:
            break
        if not set(s) <= nfa.alphabet:
            print(f"  Simbol tidak valid. Alfabet: {sorted(nfa.alphabet)}")
            continue
        print(f"  NFA: {'DITERIMA' if nfa.accepts(s) else 'DITOLAK'} | "
              f"DFA: {'DITERIMA' if dfa.accepts(s) else 'DITOLAK'}")


if __name__ == "__main__":
    main()
