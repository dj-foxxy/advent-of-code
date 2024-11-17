#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
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


def directions(input_path: Path) -> Iterator[Literal[1, -1]]:
    return (1 if token == '(' else -1 for token in input_path.read_text())


def part_1(directions: Iterable[int]) -> int:
    return sum(directions)


def part_2(directions: Iterable[int]) -> int:
    floor = 0
    for i, direction in enumerate(directions, start=1):
        floor += direction
        if floor < 0:
            return i
    raise RuntimeError()


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(directions(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
