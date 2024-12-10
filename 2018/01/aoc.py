#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import cycle
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Changes = tuple[int, ...]

type Result = int


def load_input(path: Path) -> Changes:
    with open(path) as file:
        return tuple(int(line) for line in file)


def part_1(changes: Changes) -> Result:
    return sum(changes)


def part_2(changes: Changes) -> Result:
    frequencies: set[int] = set()
    frequency = 0
    for change in cycle(changes):
        frequencies.add(frequency)
        frequency += change
        if frequency in frequencies:
            return frequency
    raise AssertionError()


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
