from typing import Tuple, List

State = Tuple[int, int, int]


def get_states(n: int) -> List[State]:
    states = []
    for blue in range(0, n + 1):
        for stars in range(0, n + 1 - blue):
            daggers = n - blue - stars
            if daggers > stars:
                continue
            states.append((blue, stars, daggers))
    return [*reversed(sorted(states))]
