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


type Input = list[list[str]]

type Result = int


def load_input(path: Path) -> Input:
    with open(path) as file:
        return [list(line.strip()) for line in file]


def match_left(grid: Input, r: int, c: int) -> bool:
    row = grid[r]
    return (
        c >= 3 and row[c - 1] == 'M' and row[c - 2] == 'A' and row[c - 3] == 'S'
    )


def match_right(grid: Input, r: int, c: int) -> bool:
    row = grid[r]
    return (
        len(row) - c >= 4
        and row[c + 1] == 'M'
        and row[c + 2] == 'A'
        and row[c + 3] == 'S'
    )


def match_down(grid: Input, r: int, c: int) -> bool:
    return (
        len(grid) - r >= 4
        and grid[r + 1][c] == 'M'
        and grid[r + 2][c] == 'A'
        and grid[r + 3][c] == 'S'
    )


def match_up(grid: Input, r: int, c: int) -> bool:
    return (
        r >= 3
        and grid[r - 1][c] == 'M'
        and grid[r - 2][c] == 'A'
        and grid[r - 3][c] == 'S'
    )


def match_up_left(grid: Input, r: int, c: int) -> bool:
    return (
        r >= 3
        and c >= 3
        and grid[r - 1][c - 1] == 'M'
        and grid[r - 2][c - 2] == 'A'
        and grid[r - 3][c - 3] == 'S'
    )


def match_up_right(grid: Input, r: int, c: int) -> bool:
    return (
        r >= 3
        and len(grid[r]) - c >= 4
        and grid[r - 1][c + 1] == 'M'
        and grid[r - 2][c + 2] == 'A'
        and grid[r - 3][c + 3] == 'S'
    )


def match_down_left(grid: Input, r: int, c: int) -> bool:
    return (
        len(grid) - r >= 4
        and c >= 3
        and grid[r + 1][c - 1] == 'M'
        and grid[r + 2][c - 2] == 'A'
        and grid[r + 3][c - 3] == 'S'
    )


def match_down_right(grid: Input, r: int, c: int) -> bool:
    return (
        len(grid) - r >= 4
        and len(grid[r]) - c >= 4
        and grid[r + 1][c + 1] == 'M'
        and grid[r + 2][c + 2] == 'A'
        and grid[r + 3][c + 3] == 'S'
    )


def part_1(input: Input) -> Result:
    result = 0
    for r in range(len(input)):
        for c in range(len(input[r])):
            if input[r][c] == 'X':
                result += sum(
                    (
                        match_left(input, r, c),
                        match_right(input, r, c),
                        match_up(input, r, c),
                        match_down(input, r, c),
                        match_up_left(input, r, c),
                        match_up_right(input, r, c),
                        match_down_left(input, r, c),
                        match_down_right(input, r, c),
                    )
                )
    return result


def match_mas(grid: Input, r: int, c: int) -> bool:
    if grid[r][c] != 'A':
        return False
    match grid[r - 1][c - 1]:
        case 'M':
            dr = 'S'
        case 'S':
            dr = 'M'
        case _:
            return False
    if grid[r + 1][c + 1] != dr:
        return False
    match grid[r - 1][c + 1]:
        case 'M':
            dl = 'S'
        case 'S':
            dl = 'M'
        case _:
            return False
    return grid[r + 1][c - 1] == dl


def part_2(input: Input) -> Result:
    result = 0
    for r in range(1, len(input) - 1):
        for c in range(1, len(input[r]) - 1):
            if match_mas(input, r, c):
                result += 1
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
