#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Sequence, Set
from dataclasses import dataclass
from itertools import permutations
import json
from pathlib import Path
from typing import Final, Literal, final


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('part', type=int, choices=(1, 2))
    parser.add_argument('input', type=Path)
    args = parser.parse_args()
    return Arguments(part=args.part, input_path=args.input)


@final
class Guest:
    def __init__(self, name: str) -> None:
        self.name: Final = name
        self.happiness: Final[dict[Guest, int]] = {}


def load_input(path: Path) -> list[Guest]:
    guests: dict[str, Guest] = {}

    def get_guest(name: str) -> Guest:
        if (guest := guests.get(name)) is None:
            guests[name] = guest = Guest(name)
        return guest

    with open(path) as file:
        for line in file:
            name, _, sign, value, _, _, _, _, _, _, other_name = line.split()
            guest = get_guest(name)
            other = get_guest(other_name.rstrip('.'))
            guest.happiness[other] = {'gain': 1, 'lose': -1}[sign] * int(value)
    return list(guests.values())


def sum_happiness(plan: Sequence[Guest]) -> int:
    total = 0
    for i, guest in enumerate(plan):
        back = guest.happiness[plan[i - 1]]
        forw = guest.happiness[plan[(i + 1) % len(plan)]]
        total += back + forw
    return total


def part_1(guests: list[Guest]) -> int:
    return max(sum_happiness(plan) for plan in permutations(guests))


def part_2(guests: list[Guest]) -> int:
    me = Guest('Me')
    for guest in guests:
        me.happiness[guest] = guest.happiness[me] = 0
    guests.append(me)
    return part_1(guests)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_input(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
