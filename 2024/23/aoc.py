#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, final

from rich import print


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
@dataclass(frozen=True, slots=True)
class Computer:
    name: Final[str]
    neighbors: Final[set['Computer']] = field(
        default_factory=set,
        repr=False,
        compare=False,
    )


type Computers = dict[str, Computer]


def load_computers(path: Path) -> Computers:
    computers: dict[str, Computer] = {}

    def get_computer(name: str) -> Computer:
        computer = computers.get(name)
        if computer is None:
            computer = computers[name] = Computer(name)
        return computer

    with open(path) as file:
        for line in file:
            name_a, name_b = line.rstrip('\n').split('-')
            computer_a = get_computer(name_a)
            computer_b = get_computer(name_b)
            computer_a.neighbors.add(computer_b)
            computer_b.neighbors.add(computer_a)

    return computers


type Result = int


def part_1(computers: Computers) -> Result:
    loops: set[frozenset[Computer]] = set()
    for computer_a in computers.values():
        for computer_b in computer_a.neighbors:
            for computer_c in computer_b.neighbors:
                if computer_a in computer_c.neighbors:
                    loops.add(frozenset((computer_a, computer_b, computer_c)))
    return sum(
        any(computer.name.startswith('t') for computer in loop)
        for loop in loops
    )


def part_2(input: Computers) -> Result:
    return 0


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_computers(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
