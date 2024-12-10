#!/usr/bin/python
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from types import coroutine
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


type Input = tuple[int, int, Mapping[int, Sequence[tuple[int, int]]]]

type Result = int


def load_input(path: Path) -> Input:
    antennas: defaultdict[int, list[tuple[int, int]]] = defaultdict(list)
    y = x = None
    with open(path) as file:
        for y, line in enumerate(file):
            for x, token in enumerate(line.strip()):
                if token != '.':
                    antennas[ord(token)].append((x, y))
    if y is None or x is None:
        raise ValueError()
    return (
        x + 1,
        y + 1,
        {freq: tuple(coords) for freq, coords in antennas.items()},
    )


def part_1(input: Input) -> Result:
    w, h, antennas = input
    antinodes: set[tuple[int, int]] = set()
    for coords in antennas.values():
        for i, (x1, y1) in enumerate(coords):
            for j, (x2, y2) in enumerate(coords):
                if i != j:
                    x = 2 * x2 - x1
                    y = 2 * y2 - y1
                    if 0 <= x < w and 0 <= y < h:
                        antinodes.add((x, y))
    return len(antinodes)


def part_2(input: Input) -> Result:
    w, h, antennas = input
    antinodes: set[tuple[int, int]] = set()
    for coords in antennas.values():
        for i, (x1, y1) in enumerate(coords):
            for j, (x2, y2) in enumerate(coords):
                if i != j:
                    dx = x2 - x1
                    dy = y2 - y1
                    for k in count(1):
                        x = x1 + k * dx
                        y = y1 + k * dy
                        if 0 <= x < w and 0 <= y < h:
                            antinodes.add((x, y))
                        else:
                            break
    return len(antinodes)


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
