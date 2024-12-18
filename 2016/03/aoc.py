#!/usr/bin/python
from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, kw_only=True, slots=True)
class Arguments:
    part: Literal[1, 2]
    input_path: Path


def parse_args() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument('-p', '--part', default=1, choices=(1, 2), type=int)
    parser.add_argument('-i', '--input', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Result = int


def part_1(path: Path) -> Result:
    with open(path) as file:
        return sum(
            a + b > c
            for a, b, c in (
                sorted((int(a), int(b), int(c)))
                for a, b, c in (line.strip().split() for line in file)
            )
        )


def part_2(input: Input) -> Result:
    return 0


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(args.input_path))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
