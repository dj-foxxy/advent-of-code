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


type Step = tuple[Literal[1, 0, -1], Literal[1, 0, -1]]

type Input = tuple[tuple[Step, ...], ...]

type Result = str


def load_input(path: Path) -> Input:
    steps: dict[str, Step] = {
        'U': (0, -1),
        'D': (0, 1),
        'L': (-1, 0),
        'R': (1, 0),
    }
    with open(path) as file:
        return tuple(
            tuple(steps[token] for token in line.strip()) for line in file
        )


def clamp(value: int) -> int:
    return max(0, min(value, 2))


def part_1(input: Input) -> Result:
    x = y = 1
    code = ''
    for steps in input:
        for dx, dy in steps:
            x = clamp(x + dx)
            y = clamp(y + dy)
        code += str(y * 3 + x + 1)
    return code


PAD: Final = (
    (0, 0,   0,   0,   0, 0, 0),
    (0, 0,   0,   1,   0, 0, 0),
    (0, 0,   2,   3,   4, 0, 0),
    (0, 5,   6,   7,   8, 9, 0),
    (0, 0, 0xA, 0xB, 0xC, 0, 0),
    (0, 0,   0, 0xD,   0, 0, 0),
    (0, 0,   0,   0,   0, 0, 0),
)


def part_2(input: Input) -> Result:
    x = 1
    y = 3
    code = ''
    for steps in input:
        for dx, dy in steps:
            next_x = x + dx
            next_y = y + dy
            if PAD[next_y][next_x]:
                x = next_x
                y = next_y
        code += f'{PAD[y][x]:X}'
    return code


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
