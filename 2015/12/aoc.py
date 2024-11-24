#!/usr/bin/env python
from argparse import ArgumentParser
from collections.abc import Set
from dataclasses import dataclass
import json
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


def load_input(path: Path) -> object:
    with open(path) as file:
        return json.load(file)


def traverse(input: object, skip_dict_values: Set[str] = set()) -> int:
    t = lambda child: traverse(child, skip_dict_values)
    match input:
        case dict() as dict_input:
            if skip_dict_values:
                for value in dict_input.values():
                    if isinstance(value, str) and value in skip_dict_values:
                        return 0
            return sum(t(value) for value in dict_input.values())
        case int() as int_input:
            return int_input
        case list():
            return sum(t(item) for item in input)
        case str():
            return 0
        case _:
            raise TypeError(input)


def part_1(input: object) -> int:
    return traverse(input)


def part_2(input: object) -> int:
    return traverse(input, frozenset(('red',)))


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
