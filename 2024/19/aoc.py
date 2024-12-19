#!/usr/bin/python
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
    parser.add_argument('part', default=1, choices=(1, 2), type=int)
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


@final
class Input(NamedTuple):
    towels: tuple[str, ...]
    designs: tuple[str, ...]


def load_input(path: Path) -> Input:
    with open(path) as file:
        towels = tuple(file.readline().rstrip().split(', '))
        file.readline()
        designs = tuple(line.rstrip() for line in file)
    return Input(towels, designs)


type Result = int


def is_possible(design: str, towels: tuple[str, ...]) -> bool:
    return not design or any(
        design.startswith(towel) and is_possible(design[len(towel) :], towels)
        for towel in towels
    )


def part_1(input: Input) -> Result:
    return sum(is_possible(design, input.towels) for design in input.designs)


def _count_solutions(design: str, towels: tuple[str, ...]) -> int:
    if design:
        return sum(
            count_solutions(design[len(towel) :], towels)
            for towel in towels
            if design.startswith(towel)
        )
    else:
        return 1


cache: dict[str, int] = {}


def count_solutions(design: str, towels: tuple[str, ...]) -> int:
    count = cache.get(design)
    if count is None:
        count = _count_solutions(design, towels)
        cache[design] = count
    return count


def part_2(input: Input) -> Result:
    return sum(
        count_solutions(design, input.towels) for design in input.designs
    )


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
