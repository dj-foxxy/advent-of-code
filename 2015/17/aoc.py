#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, final


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


def load_input(path: Path) -> tuple[int, ...]:
    return tuple(map(int, path.read_text().split()))

from itertools import combinations

def part_1(caps: tuple[int, ...]) -> int:
    count = 0
    for r in range(1, len(caps) + 1):
        for cs in combinations(caps, r):
            if sum(cs) == 150:
                count += 1
    return count


def part_2(caps: tuple[int, ...]) -> int:
    count = 0
    for r in range(1, len(caps) + 1):
        for cs in combinations(caps, r):
            if sum(cs) == 150:
                count += 1
        if count:
            break
    return count


    return 0


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
