#!/usr/bin/python
from argparse import ArgumentParser
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto, unique
from pathlib import Path
from typing import Literal, final


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


type Input = tuple[tuple[int, ...], ...]

type Result = int


def load_input(path: Path) -> Input:
    with open(path) as file:
        return tuple(
            tuple(int(token) for token in line.strip().split()) for line in file
        )


@final
@unique
class State(Enum):
    START = auto()
    DETECT_DIRECTION = auto()
    DECREASING = auto()
    INCREASING = auto()


def is_safe_diff(lower_level: int, higher_level: int) -> bool:
    return 1 <= higher_level - lower_level <= 3


def is_safe(report: Iterable[int]) -> bool:
    state = State.START
    prev_level = 0
    for level in report:
        match state:
            case State.START:
                state = State.DETECT_DIRECTION
            case State.DETECT_DIRECTION:
                if level < prev_level:
                    if not is_safe_diff(level, prev_level):
                        return False
                    state = State.DECREASING
                elif level > prev_level:
                    state = State.INCREASING
                    if not is_safe_diff(prev_level, level):
                        return False
                else:
                    return False
            case State.DECREASING:
                if not is_safe_diff(level, prev_level):
                    return False
            case State.INCREASING:
                if not is_safe_diff(prev_level, level):
                    return False
        prev_level = level
    return True


def part_1(input: Input) -> Result:
    return sum(is_safe(report) for report in input)


def is_safe_allowing_single_exclusion(report: tuple[int, ...]) -> bool:
    return is_safe(report) or any(
        is_safe(report[:i] + report[i + 1 :]) for i in range(len(report))
    )


def part_2(input: Input) -> Result:
    return sum(is_safe_allowing_single_exclusion(report) for report in input)


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
