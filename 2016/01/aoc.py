#!/usr/bin/python
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal


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


type Input = list[tuple[Literal[-1, 1], int]]

type Result = int

L: Final = -1

R: Final = 1


def load_input(path: Path) -> Input:
    return [
        ((L if token[0] == 'L' else R), int(token[1:]))
        for token in path.read_text().strip().split(', ')
    ]


DIRECTIONS: Final = (
    (0, 1),  # North
    (1, 0),  # East
    (0, -1),  # South
    (-1, 0),  # West
)


def distance(x: int, y: int) -> int:
    return abs(x) + abs(y)


def part_1(input: Input) -> Result:
    x = y = facing = 0
    for turn, blocks in input:
        facing = (facing + turn) % len(DIRECTIONS)
        x_sign, y_sign = DIRECTIONS[facing]
        x += x_sign * blocks
        y += y_sign * blocks
    return distance(x, y)


def find_first_revisited(input: Input) -> tuple[int, int]:
    x = y = facing = 0
    visited: set[tuple[int, int]] = set()
    visited.add((x, y))
    for turn, blocks in input:
        facing = (facing + turn) % len(DIRECTIONS)
        x_sign, y_sign = DIRECTIONS[facing]
        if x_sign:
            for dx in range(1, blocks):
                location = x + x_sign * dx, y
                if location in visited:
                    return location
                visited.add(location)
            x += x_sign * blocks
        if y_sign:
            for dy in range(1, blocks):
                location = x, y + y_sign * dy
                if location in visited:
                    return location
                visited.add(location)
            y += y_sign * blocks
    raise ValueError()


def part_2(input: Input) -> Result:
    return distance(*find_first_revisited(input))


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
