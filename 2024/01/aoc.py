#!/usr/bin/python
from argparse import ArgumentParser
from collections import Counter
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


type Input = tuple[list[int], list[int]]

type Result = int


def load_input(path: Path) -> Input:
    list_1: list[int] = []
    list_2: list[int] = []
    with open(path) as file:
        for line in file:
            token_1, token_2 = line.split()
            list_1.append(int(token_1))
            list_2.append(int(token_2))
    return list_1, list_2


def part_1(input: Input) -> Result:
    list_1, list_2 = input
    list_1.sort()
    list_2.sort()
    return sum(abs(item_2 - item_1) for item_1, item_2 in zip(list_1, list_2))


def part_2(input: Input) -> Result:
    list_1, list_2 = input
    counter = Counter(list_2)
    return sum(item_1 * counter.get(item_1, 0) for item_1 in list_1)


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
