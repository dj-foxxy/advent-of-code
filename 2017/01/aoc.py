#!/usr/bin/python
from argparse import ArgumentParser
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


type Input = str

type Result = int


def load_input(path: Path) -> Input:
    return path.read_text().strip()


def part_1(input: Input) -> Result:
    count = len(input)
    input += input[0]
    return sum(
        (int(input[i]) if input[i] == input[i + 1] else 0) for i in range(count)
    )


def part_2(input: Input) -> Result:
    length = len(input)
    offset = length // 2
    result = 0
    for i, c in enumerate(input):
        if c == input[(i + offset) % length]:
            result += int(c)
    return result


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
