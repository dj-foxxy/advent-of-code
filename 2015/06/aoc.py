#!/usr/bin/env python
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum, auto, unique
from pathlib import Path
from typing import Literal, NamedTuple, final

from rich import print


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


@final
@unique
class Action(Enum):
    OFF = auto()
    ON = auto()
    TOGGLE = auto()


@final
class Cell(NamedTuple):
    x: int
    y: int


def parse_cell(text: str) -> Cell:
    return Cell(*map(int, text.split(',')))


@final
class Instruction(NamedTuple):
    action: Action
    start: Cell
    end: Cell


def parse_instruction(text: str) -> Instruction:
    state = 0
    action = start = end = None
    for token in text.split():
        match state:
            case 0:
                match token:
                    case 'turn':
                        state = 1
                    case 'toggle':
                        action = Action.TOGGLE
                        state = 2
                    case _:
                        raise ValueError()
            case 1:
                match token:
                    case 'off':
                        action = Action.OFF
                        state = 2
                    case 'on':
                        action = Action.ON
                        state = 2
                    case _:
                        raise ValueError()
            case 2:
                start = parse_cell(token)
                state = 3
            case 3:
                state = 4
            case 4:
                end = parse_cell(token)
                state = 5
            case _:
                raise ValueError()
    if action is None:
        raise ValueError()
    if start is None:
        raise ValueError()
    if end is None:
        raise ValueError()
    return Instruction(action, start, end)


def load_instructions(path: Path):
    with open(path) as file:
        return [parse_instruction(line) for line in file]


def part_1(instructions: list[Instruction]) -> int:
    grid = [[False] * 1000 for _ in range(1000)]
    count = 0
    for action, start, end in instructions:
        for y in range(start.y, end.y + 1):
            row = grid[y]
            for x in range(start.x, end.x + 1):
                state = row[x]
                match action:
                    case Action.OFF:
                        if state:
                            state = False
                            count -= 1
                    case Action.ON:
                        if not state:
                            state = True
                            count += 1
                        state = True
                    case Action.TOGGLE:
                        if state:
                            state = False
                            count -= 1
                        else:
                            state = True
                            count += 1
                row[x] = state
    return count


def part_2(instructions: list[Instruction]) -> int:
    grid = [[0] * 1000 for _ in range(1000)]
    total_brightness = 0
    for action, start, end in instructions:
        for y in range(start.y, end.y + 1):
            row = grid[y]
            for x in range(start.x, end.x + 1):
                brightness = row[x]
                match action:
                    case Action.OFF:
                        if brightness:
                            brightness -= 1
                            total_brightness -= 1
                    case Action.ON:
                        brightness += 1
                        total_brightness += 1
                    case Action.TOGGLE:
                        brightness += 2
                        total_brightness += 2
                row[x] = brightness
    return total_brightness


def main() -> None:
    args = parse_args()
    match args.part:
        case 1:
            part = part_1
        case 2:
            part = part_2
    print(part(load_instructions(args.input_path)))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(1)
