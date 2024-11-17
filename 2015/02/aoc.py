#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NamedTuple, final


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
class Present(NamedTuple):
    l: int
    w: int
    h: int


type Data = list[Present]


def load_data(path: Path) -> Data:
    with open(path) as file:
        return [Present(*map(int, line.split('x'))) for line in file]


def calculate_required_wrapping_paper(present: Present) -> int:
    l, w, h = present
    lw = l * w
    wh = w * h
    hl = h * l
    return 2 * (lw + wh + hl) + min(lw, wh, hl)


def part_1(data: Data) -> int:
    return sum(calculate_required_wrapping_paper(present) for present in data)


def calculate_required_ribbon(present: Present) -> int:
    d1, d2, d3 = sorted(present)
    return 2 * (d1 + d2) + (d1 * d2 * d3)


def part_2(data: Data) -> int:
    return sum(calculate_required_ribbon(present) for present in data)


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_data(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
