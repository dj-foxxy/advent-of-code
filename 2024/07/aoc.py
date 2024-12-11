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
    parser.add_argument('input', nargs='?', type=Path)
    args = parser.parse_args()
    if args.input is None:
        input_path = Path(__file__).resolve(strict=True).parent / 'input'
    else:
        input_path = args.input
    return Arguments(part=args.part, input_path=input_path)


type Input = tuple[tuple[int, tuple[int, ...]], ...]

type Result = int


def load_input(path: Path) -> Input:
    input: list[tuple[int, tuple[int, ...]]] = []
    with open(path) as file:
        for line in file:
            value, tail = line.split(':')
            input.append((int(value), tuple(map(int, tail.split()))))
    if any(operand <= 0 for _, operands in input for operand in operands):
        raise ValueError()
    return tuple(input)


def is_feasible_v1(value: int, operands: tuple[int, ...], i: int) -> bool:
    i -= 1
    operand = operands[i]

    if not i:
        return value == operand

    if is_feasible_v1(value - operand, operands, i):
        return True

    next_value, remainder = divmod(value, operand)
    return not remainder and is_feasible_v1(int(next_value), operands, i)


def part_1(input: Input) -> Result:
    return sum(
        value
        for value, operands in input
        if is_feasible_v1(value, operands, len(operands))
    )


def is_feasible_v2(value: int, operands: tuple[int, ...], i: int) -> bool:
    i -= 1
    operand = operands[i]

    if not i:
        return value == operand

    # + Operator
    if operand < value and is_feasible_v2(value - operand, operands, i):
        return True

    # * Operator
    next_value, remainder = divmod(value, operand)

    if not remainder and is_feasible_v2(next_value, operands, i):
        return True

    # Concat Operator
    if value <= 9:
        return False

    value_str = str(value)
    operand_str = str(operand)

    return value_str.endswith(operand_str) and is_feasible_v2(
        int(value_str.removesuffix(operand_str)),
        operands,
        i,
    )


def part_2(input: Input) -> Result:
    return sum(
        value
        for value, operands in input
        if is_feasible_v2(value, operands, len(operands))
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
