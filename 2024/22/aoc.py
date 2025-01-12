#!/usr/bin/python
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
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Input = tuple[int, ...]


def load_input(path: Path) -> Input:
    with open(path) as file:
        return tuple(int(line) for line in file)


type Result = int


def part_1(input: Input) -> Result:
    result = 0
    for i in input:
        for _ in range(2000):
            i = (i ^ (i << 6)) & 16777215
            i = (i ^ (i >> 5)) & 16777215
            i = (i ^ (i << 11)) & 16777215
        result += i
    return result


def part_2(input: Input) -> Result:
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
